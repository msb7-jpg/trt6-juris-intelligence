# Docker‑E2E Workers Implementation Plan

> **For agentic workers:** REQUIRED SUB‑SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task‑by‑task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the full TRT6 pipeline in Docker Compose with two Celery workers (scrapper + LLM) that communicate via RabbitMQ, store files in MinIO, and expose a deduplication step.

**Architecture:**
- `docker compose` starts PostgreSQL, RabbitMQ, MinIO, the Django API, a *scrapper* worker, an *LLM* worker, and an on‑demand *ingestion* job.
- The scrapper worker creates PDF files and dispatches a Celery task to the LLM worker.
- The LLM worker calls the external LM Studio endpoint (`host.docker.internal:1234/v1`).
- After LLM analysis, a deduplication task runs (via the same Celery app) to clean up duplicate PDFs.

**Tech Stack:** Docker Compose, Python 3.13, `uv`, Django + DRF, Celery + RabbitMQ, MinIO, Playwright (scrapper), pytest.

---

### Task 1: Common Celery Entrypoint

**Files**
- Create: `docker/entrypoints/celery.sh`

- [ ] **Step 1: Write entrypoint script**

```bash
#!/usr/bin/env bash
set -euo pipefail

# Required environment variables
APP_MODULE=${APP_MODULE:?APP_MODULE is required}
QUEUE=${QUEUE:?QUEUE is required}

uv run celery -A "$APP_MODULE" worker -l info -Q "$QUEUE"
```

- [ ] **Step 2: Make script executable**

```bash
chmod +x docker/entrypoints/celery.sh
```

- [ ] **Step 3: Commit**

```bash
git add docker/entrypoints/celery.sh
git commit -m "feat: common Celery entrypoint for workers"
```

---

### Task 2: Scrapper Worker Dockerfile

**Files**
- Create: `apps/worker-scrapper/Dockerfile`

- [ ] **Step 1: Write Dockerfile**

```dockerfile
FROM python:3.13-slim

# Pull uv binary
COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /uvx /bin/

WORKDIR /app

# System deps for Playwright
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libnss3 libatk-bridge2.0-0 libxkbcommon0 libxcomposite1 \
        libxrandr2 libxdamage1 libgbm1 libasound2 libxshmfence1 \
        libgtk-3-0 libdrm2 libxfixes3 && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY pyproject.toml uv.lock /app/
COPY shared/ /app/shared/
COPY apps/worker-scrapper/ /app/apps/worker-scrapper/

RUN uv sync --frozen --no-dev

# Playwright browsers
RUN uv run python -m playwright install --with-deps chromium

# Celery entrypoint
COPY docker/entrypoints/celery.sh /entrypoints/celery.sh
RUN chmod +x /entrypoints/celery.sh

ENV APP_MODULE=shared.celery_client
ENV QUEUE=scrapper_queue

CMD ["/entrypoints/celery.sh"]
```

- [ ] **Step 2: Build image locally (verify)**

```bash
docker build -f apps/worker-scrapper/Dockerfile . -t trt6-worker-scrapper:dev
```

- [ ] **Step 3: Commit**

```bash
git add apps/worker-scrapper/Dockerfile
git commit -m "feat: Dockerfile for scrapper worker"
```

---

### Task 3: LLM Worker Dockerfile

**Files**
- Create: `apps/worker-llm/Dockerfile`

- [ ] **Step 1: Write Dockerfile**

```dockerfile
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock /app/
COPY shared/ /app/shared/
COPY apps/worker-llm/ /app/apps/worker-llm/

RUN uv sync --frozen --no-dev

COPY docker/entrypoints/celery.sh /entrypoints/celery.sh
RUN chmod +x /entrypoints/celery.sh

ENV APP_MODULE=shared.celery_client
ENV QUEUE=llm_queue

CMD ["/entrypoints/celery.sh"]
```

- [ ] **Step 2: Build image locally**

```bash
docker build -f apps/worker-llm/Dockerfile . -t trt6-worker-llm:dev
```

- [ ] **Step 3: Commit**

```bash
git add apps/worker-llm/Dockerfile
git commit -m "feat: Dockerfile for LLM worker"
```

---

### Task 4: Ingestion Service Dockerfile

**Files**
- Create: `apps/ingestion/Dockerfile`

- [ ] **Step 1: Write Dockerfile**

```dockerfile
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock /app/
COPY shared/ /app/shared/
COPY apps/ingestion/ /app/apps/ingestion/
COPY apps/worker-scrapper/ /app/apps/worker-scrapper/

RUN uv sync --frozen --no-dev

WORKDIR /app/apps/ingestion
CMD ["uv", "run", "ingest", "--provider", "file", "--trigger"]
```

- [ ] **Step 2: Build image locally**

```bash
docker build -f apps/ingestion/Dockerfile . -t trt6-ingestion:dev
```

- [ ] **Step 3: Commit**

```bash
git add apps/ingestion/Dockerfile
git commit -m "feat: Dockerfile for ingestion job"
```

---

### Task 5: Update Celery Configuration for Routing

**Files**
- Modify: `shared/src/shared/celery_client.py`

- [ ] **Step 1: Add routing table**

```python
app.conf.task_routes = {
    "pje_scraper.worker.run_pipeline": {"queue": "scrapper_queue"},
    "worker_llm.run_pipeline": {"queue": "llm_queue"},
    "pje_scraper.deduplication.run": {"queue": "scrapper_queue"},
}
```

- [ ] **Step 2: Verify broker URL uses env var (already present).**

- [ ] **Step 3: Run full test suite**

```bash
cd apps/api && uv run pytest -q
```

- [ ] **Step 4: Commit**

```bash
git add shared/src/shared/celery_client.py
git commit -m "fix: Celery routing for scrapper, LLM and deduplication"
```

---

### Task 6: Add Deduplication Task

**Files**
- Create: `apps/worker-scrapper/deduplication.py`
- Modify: `apps/worker-scrapper/main.py`
- Create test: `apps/worker-scrapper/tests/test_deduplication.py`

- [ ] **Step 1: Write minimal deduplication task**

```python
from shared.celery_client import app

@app.task(name="pje_scraper.deduplication.run")
def deduplicate_processos():
    """Simple placeholder deduplication:
    - list objects in MinIO bucket `pje-documents`
    - delete any duplicate filenames (keep first)
    """
    from shared.s3_client import get_s3_client
    client = get_s3_client()
    bucket = "pje-documents"
    objs = client.list_objects(bucket)
    seen = set()
    for obj in objs:
        name = obj.object_name
        if name in seen:
            client.delete_object(bucket, name)
        else:
            seen.add(name)
```

- [ ] **Step 2: Invoke from scrapper pipeline** (append to `apps/worker-scrapper/main.py` after upload)

```python
from .deduplication import deduplicate_processos

deduplicate_processos.delay()
```

- [ ] **Step 3: Write pytest**

```python
def test_deduplicate_processos(monkeypatch):
    class DummyClient:
        def __init__(self):
            self.deleted = []
        def list_objects(self, bucket):
            from collections import namedtuple
            Obj = namedtuple("Obj", "object_name")
            return [Obj("a.pdf"), Obj("b.pdf"), Obj("a.pdf")]
        def delete_object(self, bucket, name):
            self.deleted.append(name)
    monkeypatch.setattr("shared.s3_client.get_s3_client", lambda: type("X", (), {"client": DummyClient()}))
    from apps.worker-scrapper.deduplication import deduplicate_processos
    deduplicate_processos()
    assert "a.pdf" in deduplicate_processos.__globals__["get_s3_client"]().client.deleted
```

- [ ] **Step 4: Run test**

```bash
cd apps/worker-scrapper && uv run pytest -q
```

- [ ] **Step 5: Commit**

```bash
git add apps/worker-scrapper/deduplication.py apps/worker-scrapper/main.py apps/worker-scrapper/tests/test_deduplication.py
git commit -m "feat: deduplication task invoked by scrapper"
```

---

### Task 7: Compose Stack – Wire Everything Together

**Files**
- Modify: `compose.yaml`

- [ ] **Step 1: Add services**

```yaml
version: "3.9"

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: trt6
      POSTGRES_USER: trt6
      POSTGRES_PASSWORD: trt6
    volumes:
      - postgres_data:/var/lib/postgresql/data

  rabbitmq:
    image: rabbitmq:3-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: user
      RABBITMQ_DEFAULT_PASS: password

  minio:
    image: minio/minio
    command: server /data
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  api:
    build:
      context: .
      dockerfile: apps/api/Dockerfile
    environment:
      POSTGRES_HOST: postgres
      POSTGRES_DB: trt6
      POSTGRES_USER: trt6
      POSTGRES_PASSWORD: trt6
      CELERY_BROKER_URL: amqp://user:password@rabbitmq:5672//
      S3_ENDPOINT: minio:9000
      S3_ACCESS_KEY: minioadmin
      S3_SECRET_KEY: minioadmin
      S3_SECURE: "false"
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - rabbitmq
      - minio

  worker-scrapper:
    build:
      context: .
      dockerfile: apps/worker-scrapper/Dockerfile
    environment:
      CELERY_BROKER_URL: amqp://user:password@rabbitmq:5672//
      S3_ENDPOINT: minio:9000
      S3_ACCESS_KEY: minioadmin
      S3_SECRET_KEY: minioadmin
      S3_SECURE: "false"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - api
      - rabbitmq
      - minio

  worker-llm:
    build:
      context: .
      dockerfile: apps/worker-llm/Dockerfile
    environment:
      CELERY_BROKER_URL: amqp://user:password@rabbitmq:5672//
      S3_ENDPOINT: minio:9000
      S3_ACCESS_KEY: minioadmin
      S3_SECRET_KEY: minioadmin
      S3_SECURE: "false"
      WORKER_LLM_BASE_URL: http://host.docker.internal:1234/v1
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - api
      - rabbitmq
      - minio

  ingestion:
    build:
      context: .
      dockerfile: apps/ingestion/Dockerfile
    environment:
      CELERY_BROKER_URL: amqp://user:password@rabbitmq:5672//
      S3_ENDPOINT: minio:9000
      S3_ACCESS_KEY: minioadmin
      S3_SECRET_KEY: minioadmin
      S3_SECURE: "false"
    depends_on:
      - api
      - rabbitmq
      - minio

volumes:
  postgres_data:
  minio_data:
```

- [ ] **Step 2: Sanity‑check compose**

```bash
docker compose config -q
```

- [ ] **Step 3: Commit**

```bash
git add compose.yaml
git commit -m "feat: compose stack for full Docker E2E (workers, api, ingest)"
```

---

### Task 8: Documentation – Setup & Runbook

**Files**
- Create: `docs/pipeline-e2e-docker-runbook.md`

- [ ] **Step 1: Write markdown**

```markdown
# Docker E2E Runbook (TRT6)

## Prerequisites
- Docker ≥ 24, Docker Compose ≥ 2.20
- LM Studio (or any OpenAI‑compatible server) listening at `http://localhost:1234/v1` on the host.
- `uv` is bundled in the images; no local Python install required.

## Start the stack
```bash
docker compose up -d --build
```

## Trigger ingestion (creates the initial batch of PDFs)
```bash
docker compose run --rm ingestion
```

## Expected flow
1. **scrapper** reads source files, uploads PDFs to MinIO, and enqueues `worker_llm.run_pipeline` on queue `llm_queue`.
2. **worker‑llm** contacts `host.docker.internal:1234/v1`, stores the analysis result via the API, then the scrapper’s deduplication task runs.
3. **API** writes results to PostgreSQL; you can query them via:
   ```bash
   curl -s http://localhost:8000/api/processos/
   ```

## Verify
- API reachable: `http://localhost:8000/api/processos/`
- MinIO console: `http://localhost:9001` (user / pass = `minioadmin/minioadmin`)
  - Bucket `pje-documents` should contain PDFs.
- Logs (tail in separate terminals):
  ```bash
  docker compose logs -f worker-scrapper
  docker compose logs -f worker-llm
  docker compose logs -f api
  ```

## Clean up
```bash
docker compose down -v   # removes containers and volumes
```
```

- [ ] **Step 2: Commit**

```bash
git add docs/pipeline-e2e-docker-runbook.md
git commit -m "docs: Docker E2E runbook"
```

---

### Task 9: Verify End‑to‑End Locally

- [ ] **Step 1: Bring stack up**
```bash
docker compose up -d --build
```
- [ ] **Step 2: Run ingestion**
```bash
docker compose run --rm ingestion
```
- [ ] **Step 3: Observe logs** (ensure scrapper → LLM → deduplication flow).
- [ ] **Step 4: Query API**
```bash
curl -s http://localhost:8000/api/processos/nao_poss...
```
- [ ] **Step 5: Iterate on any failing service, re‑run its tests, and repeat.
- [ ] **Step 6: When the full pipeline succeeds, optionally tag the commit.
- [ ] **Step 7: Commit final tweaks**
```bash
git add .
git commit -m "chore: final E2E verification fixes"
```

---

*All tasks are ready to be executed. Choose a execution mode (sub‑agent or inline) when you are ready to start.*