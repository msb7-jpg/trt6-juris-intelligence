# Event‑Driven Refactor Plan for Ingestion ↔ Scraper

## Why change?
- **Current coupling**: `apps/ingestion` imports the full `worker‑scrapper` code (`run_pipeline`). This pulls heavy dependencies (Playwright, Selenium, OpenCV) into the ingestion image, inflating build time and container size.
- **Build impact**: Every change in the scraper forces a rebuild of the ingestion image because the whole scraper repo is copied into the ingestion Docker context.
- **Cold‑start latency**: The ingestion worker loads the entire scraper module only to invoke a single function, then discards most of it.

## Goal
Replace the direct import with an **asynchronous, event‑driven** approach using the existing **Celery + RabbitMQ** infrastructure. Ingestion will **publish a task**; the scraper worker will **consume** it, run the heavy pipeline, and optionally return results.

---

## 1. Add a Celery task to the scraper package
**File:** `apps/worker-scrapper/pje_scraper/tasks.py`
```python
from celery import shared_task

@shared_task(bind=True, name="scraper.run_pipeline")
def run_pipeline(self, payload: dict) -> dict:
    """Celery task wrapper around the existing pipeline.
    *payload* is the JSON that would have been passed directly to
    `pje_scraper.worker.run_pipeline`. The function returns a JSON‑serialisable
    dictionary that Celery will send back to the caller.
    """
    # Local import keeps heavy deps out of the worker‑process startup.
    from .worker import run_pipeline as _run
    result = _run(payload)
    return result
```
* The heavy imports (`playwright`, `opencv`, etc.) stay inside the task body, so they are only loaded when the **scraper worker** actually executes the task.
* No code changes are required in the original `run_pipeline` implementation.

---

## 2. (Optional) Thin HTTP wrapper in the API
If you want external callers to trigger the scrape via REST, expose two endpoints.
**File:** `apps/api/api/views.py`
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
from shared.celery_client import app as celery_app

@api_view(["POST"])
def launch_scraper(request):
    task = celery_app.send_task("scraper.run_pipeline", args=[request.data])
    return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)

@api_view(["GET"])
def task_status(request, task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if result.ready():
        return Response({"status": "done", "result": result.result})
    return Response({"status": result.status})
```
Add URLs in `api/urls.py`:
```python
urlpatterns += [
    path('scrape/', launch_scraper),
    path('scrape/status/<str:task_id>/', task_status),
]
```
*The API now returns a task ID immediately; callers can poll or use websockets for notifications.*

---

## 3. Refactor the ingestion code to fire‑and‑forget
**File:** `apps/ingestion/src/ingestion/submitter.py`
```python
from shared.celery_client import app as celery_app

class ProcessSubmitter:
    def __init__(self, *, base_url: str | None = None):
        self.base_url = base_url or env_manager.get_api_base_url().rstrip('/')
        self.dedup_url = f"{self.base_url}/api/processos/deduplicar/"
        self.pending_url = f"{self.base_url}/api/processos/nao_possuem_pdf/"

    # … existing submit()/fetch_pending_pdf() stay unchanged …

    def launch_scraper(self, payload: dict) -> str:
        """Schedule the heavy scraper pipeline.
        Returns the Celery task id so the caller can track progress.
        """
        task = celery_app.send_task("scraper.run_pipeline", args=[payload])
        return task.id
```
*No `import pje_scraper` any more – the ingestion image only needs the tiny Celery client.*

---

## 4. Dockerfile simplification for the ingestion service
**File:** `apps/ingestion/Dockerfile`
- **Remove** the lines that copy the scraper code:
```dockerfile
#   COPY apps/worker-scrapper/ /app/apps/worker-scrapper/   # ← delete
#   COPY . /app/                                      # ← keep only its own workspace
```
- Keep the existing `COPY pyproject.toml uv.lock /app/` and `COPY shared/ …` so the ingestion image stays lightweight (only its own dependencies).
- Re‑run `uv sync` as before – the scraper’s heavy wheels are no longer pulled into this image.

---

## 5. Environment variables (optional)
If you prefer to configure the base API URL only once, keep the existing `API_BASE_URL` env var (default `http://api:8000`). No extra variables are needed for the task communication because Celery already shares the same broker.

---

## 6. Result handling options
| Option | Description |
|--------|-------------|
| **Polling** | After `launch_scraper` you receive a `task_id`. Ingestion can call a lightweight status endpoint (`/scrape/status/<task_id>/`) until the task reports `DONE`. Simple, works with HTTP.
| **Callback/Webhook** | The scraper task, when finished, can emit a second Celery task (e.g., `ingestion.process_result`) that an ingestion worker listens for. Eliminates polling but adds a consumer.
| **Result backend** | Keep the Celery result backend (e.g., Redis) and have ingestion fetch the result directly with `AsyncResult(task_id).result`. This is essentially the same as polling but hides the HTTP layer.

Choose the simplest approach that meets your latency requirements.

---

## 7. Checklist for implementation
- [ ] Create `apps/worker-scrapper/pje_scraper/tasks.py` with the Celery wrapper.
- [ ] (Optional) Add the two API views and URLs.
- [ ] Update `apps/ingestion/src/ingestion/submitter.py` to use `celery_app.send_task`.
- [ ] Remove scraper `COPY` statements from `apps/ingestion/Dockerfile` and rebuild the image.
- [ ] Verify that the ingestion container starts quickly and can schedule a scrape without importing heavy deps.
- [ ] Test the whole flow:
  1. Ingestion calls `launch_scraper` → receives a `task_id`.
  2. Scraper worker consumes the task and runs the pipeline.
  3. Poll the status endpoint (or fetch the result via Celery) and confirm the payload.
- [ ] Clean up any stale imports or unused packages in the ingestion image.

---

## 8. Expected impact
| Metric | Before | After |
|--------|--------|-------|
| **Ingestion image size** | ~**500 MB** (includes Playwright browsers, OpenCV, Selenium) | ~**150 MB** (only ingestion deps) |
| **Docker‑build time** | > 7 min (full scraper install) | < 2 min (scraper removed) |
| **Cold‑start latency** | ~3 s (imports heavy libs) | < 1 s (Celery client only) |
| **Scalability** | Single container does both ingest & scrape → limited scaling | Independent scraper workers can be scaled horizontally without touching ingestion |

---

## 9. TL;DR
1. **Add a Celery task** (`scraper.run_pipeline`) inside the scraper repo.
2. **Make ingestion fire the task** via `celery_app.send_task` (no direct imports).
3. **Optional REST endpoints** expose the async call and status.
4. **Trim the ingestion Dockerfile** – drop the scraper copy.
5. **Deploy** and enjoy faster builds, smaller images, and independent scaling.

---

Feel free to adjust the result‑handling strategy (polling vs. callback) based on your monitoring needs.
