# Pipeline Docker E2E Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the full TRT6 pipeline (API + scrapper worker + LLM worker + infra) fully in Docker Compose with Postgres, split Celery queues, and validate end-to-end output.

**Architecture:** Docker Compose runs `postgres`, `rabbitmq`, `minio`, `api` (Django), `worker-scrapper` (Celery), `worker-llm` (Celery), and an on-demand `ingestion` job. Celery is routed to `scrapper_queue` and `llm_queue`. `worker-llm` calls an OpenAI-compatible LM Studio endpoint running on the host via `host.docker.internal`.

**Tech Stack:** Docker/Compose, uv, Django/DRF, Celery + RabbitMQ, MinIO, Postgres, Playwright.

---

## File/Module Map

- Create: `compose.yaml` updates
- Create: `apps/api/Dockerfile`
- Create: `apps/worker-scrapper/Dockerfile`
- Create: `apps/worker-llm/Dockerfile`
- Create: `apps/ingestion/Dockerfile`
- Create: `docker/entrypoints/api.sh`
- Create: `docker/entrypoints/celery.sh`
- Modify: `shared/src/shared/celery_client.py` (broker URL + routing)
- Modify: `shared/src/shared/s3_client.py` (env-configurable endpoint/creds)
- Modify: `apps/worker-llm/main.py` (fix default base_url)
- Modify: `apps/worker-llm/worker.py` (default API url uses docker hostname)
- Modify: `apps/ingestion/src/ingestion/submitter.py` (default API url uses docker hostname)
- Modify: `apps/api/api/settings.py` (Postgres via env, allowed hosts)

---

### Task 1: Make Shared Celery/S3 Config Docker-Friendly

**Files:**
- Modify: `shared/src/shared/celery_client.py`
- Modify: `shared/src/shared/s3_client.py`
- Test: `apps/api/core/tests/views/test_processo_nao_possuem_pdf.py` (add new test)

- [ ] **Step 1: Write failing test for env-configured S3 endpoint**

Add to `apps/api/core/tests/views/test_processo_nao_possuem_pdf.py`:

```python
def test_get_s3_client_uses_env_endpoint(monkeypatch):
    monkeypatch.setenv("S3_ENDPOINT", "minio:9000")
    monkeypatch.setenv("S3_ACCESS_KEY", "x")
    monkeypatch.setenv("S3_SECRET_KEY", "y")
    monkeypatch.setenv("S3_SECURE", "false")

    from shared.s3_client import get_s3_client

    client = get_s3_client()

    # MinIO keeps endpoint in a base_url object.
    base_url = getattr(client.client, "_base_url", None)
    assert base_url is not None
    assert base_url.host == "minio"
    assert base_url.port == 9000
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/api && uv run pytest core/tests/views/test_processo_nao_possuem_pdf.py -q`

Expected: FAIL because `get_s3_client()` is hardcoded to `localhost:9000`.

- [ ] **Step 3: Write minimal implementation for env-configurable S3 client**

Update `shared/src/shared/s3_client.py` to:

```python
import os

from minio import Minio
from shared.singleton import Singleton


class S3Client(metaclass=Singleton):
    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool = True) -> None:
        self.client: Minio = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def create_bucket(self, bucket_name: str) -> None:
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def upload_object(self, bucket_name: str, object_name: str, file_path: str) -> None:
        self.client.fput_object(bucket_name, object_name, file_path)

    def get_object(self, bucket_name: str, object_name: str, file_path: str) -> None:
        self.client.fget_object(bucket_name, object_name, file_path)

    def list_objects(self, bucket_name: str, prefix: str = "", recursive: bool = False) -> list:
        return list(self.client.list_objects(bucket_name, prefix=prefix, recursive=recursive))

    def delete_object(self, bucket_name: str, object_name: str) -> None:
        self.client.remove_object(bucket_name, object_name)

    def delete_bucket(self, bucket_name: str) -> None:
        self.client.remove_bucket(bucket_name)


def _env_bool(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def get_s3_client() -> S3Client:
    endpoint = os.getenv("S3_ENDPOINT", "localhost:9000")
    access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("S3_SECRET_KEY", "minioadmin")
    secure = _env_bool("S3_SECURE", "false")
    return S3Client(endpoint, access_key, secret_key, secure=secure)
```

- [ ] **Step 4: Implement Celery broker URL + routing**

Update `shared/src/shared/celery_client.py` to:

```python
import os

from celery import Celery


BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://user:password@localhost:5672//")

app = Celery("tasks", broker=BROKER_URL)

# Route tasks to dedicated queues.
app.conf.task_routes = {
    "pje_scraper.worker.run_pipeline": {"queue": "scrapper_queue"},
    "worker_llm.run_pipeline": {"queue": "llm_queue"},
}
```

- [ ] **Step 5: Run tests to verify pass**

Run: `cd apps/api && uv run pytest -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add shared/src/shared/s3_client.py shared/src/shared/celery_client.py apps/api/core/tests/views/test_processo_nao_possuem_pdf.py
git commit -m "feat: configure s3/celery via env and route queues"
```

---

### Task 2: Fix Worker Defaults for Docker Networking

**Files:**
- Modify: `apps/worker-llm/main.py`
- Modify: `apps/worker-llm/worker.py`
- Modify: `apps/ingestion/src/ingestion/submitter.py`
- Test: `apps/worker-llm/tests/test_worker.py` (add new test)

- [ ] **Step 1: Write failing test for WORKER_LLM_BASE_URL default**

Add to `apps/worker-llm/tests/test_worker.py`:

```python
def test_default_llm_base_url_is_valid(monkeypatch):
    monkeypatch.delenv("WORKER_LLM_BASE_URL", raising=False)
    from main import _build_llm
    llm = _build_llm()
    assert ":1234:1234" not in str(getattr(llm, "base_url", ""))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/worker-llm && uv run pytest -q`

Expected: FAIL due to invalid default `http://172.26.127.0:1234:1234/v1`.

- [ ] **Step 3: Fix default LLM base url**

In `apps/worker-llm/main.py`, set:

```python
base_url=os.getenv("WORKER_LLM_BASE_URL", "http://host.docker.internal:1234/v1"),
```

- [ ] **Step 4: Update worker default API url to docker hostname**

In `apps/worker-llm/worker.py`, change:

```python
DEFAULT_API_URL = "http://api:8000/api/processos/adicionar_analise/"
```

- [ ] **Step 5: Update ingestion default API urls to docker hostname**

In `apps/ingestion/src/ingestion/submitter.py`, change defaults:

```python
api_url: str = "http://api:8000/api/processos/deduplicar/",
pending_api_url: str = "http://api:8000/api/processos/nao_possuem_pdf/",
```

- [ ] **Step 6: Run tests to verify pass**

Run: `cd apps/worker-llm && uv run pytest -q`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add apps/worker-llm/main.py apps/worker-llm/worker.py apps/worker-llm/tests/test_worker.py apps/ingestion/src/ingestion/submitter.py
git commit -m "fix: docker-friendly defaults for llm and api urls"
```

---

### Task 3: Dockerize API (Multi-Stage Build + uv binary copy)

**Files:**
- Create: `apps/api/Dockerfile`
- Create: `docker/entrypoints/api.sh`
- Modify: `apps/api/api/settings.py`

- [ ] **Step 1: Update settings for Postgres via env + allow docker hostnames**

Replace DB config and set:

```python
import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "trt6"),
        "USER": os.getenv("POSTGRES_USER", "trt6"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "trt6"),
        "HOST": os.getenv("POSTGRES_HOST", "postgres"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

ALLOWED_HOSTS = ["*"]
```

- [ ] **Step 2: Create API entrypoint**

Create `docker/entrypoints/api.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd /app/apps/api

uv run python manage.py migrate --noinput
uv run python manage.py runserver 0.0.0.0:8000
```

- [ ] **Step 3: Create `apps/api/Dockerfile`**

```dockerfile
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /uvx /bin/

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock /app/
COPY shared/ /app/shared/
COPY apps/ingestion/ /app/apps/ingestion/
COPY apps/api/ /app/apps/api/

RUN uv sync --frozen --no-dev

COPY docker/entrypoints/api.sh /entrypoints/api.sh
RUN chmod +x /entrypoints/api.sh

EXPOSE 8000
CMD ["/entrypoints/api.sh"]
```

- [ ] **Step 4: Build image**

Run: `docker build -f apps/api/Dockerfile . -t trt6-api:dev`

Expected: build succeeds.

- [ ] **Step 5: Commit**

```bash
git add apps/api/Dockerfile docker/entrypoints/api.sh apps/api/api/settings.py
git commit -m "feat: dockerize api with postgres and uv"
```

---

### Task 4: Dockerize Workers + Ingestion

**Files:**
- Create: `apps/worker-scrapper/Dockerfile`
- Create: `apps/worker-llm/Dockerfile`
- Create: `apps/ingestion/Dockerfile`
- Create: `docker/entrypoints/celery.sh`

- [ ] **Step 1: Create common Celery entrypoint**

Create `docker/entrypoints/celery.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

APP_MODULE=${APP_MODULE:?APP_MODULE is required}
QUEUE=${QUEUE:?QUEUE is required}

uv run celery -A "$APP_MODULE" worker -l info -Q "$QUEUE"
```

- [ ] **Step 2: Create worker-llm Dockerfile**

Create `apps/worker-llm/Dockerfile`:

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

- [ ] **Step 3: Create worker-scrapper Dockerfile (Playwright)**

Create `apps/worker-scrapper/Dockerfile`:

```dockerfile
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /uvx /bin/

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    libnss3 libatk-bridge2.0-0 libxkbcommon0 libxcomposite1 libxrandr2 libxdamage1 \
    libgbm1 libasound2 libxshmfence1 libgtk-3-0 libdrm2 libxfixes3 \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock /app/
COPY shared/ /app/shared/
COPY apps/worker-scrapper/ /app/apps/worker-scrapper/

RUN uv sync --frozen --no-dev

RUN uv run python -m playwright install --with-deps chromium

COPY docker/entrypoints/celery.sh /entrypoints/celery.sh
RUN chmod +x /entrypoints/celery.sh

ENV APP_MODULE=shared.celery_client
ENV QUEUE=scrapper_queue

CMD ["/entrypoints/celery.sh"]
```

- [ ] **Step 4: Create ingestion Dockerfile**

Create `apps/ingestion/Dockerfile`:

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

- [ ] **Step 5: Build images**

Run:
- `docker build -f apps/worker-llm/Dockerfile . -t trt6-worker-llm:dev`
- `docker build -f apps/worker-scrapper/Dockerfile . -t trt6-worker-scrapper:dev`
- `docker build -f apps/ingestion/Dockerfile . -t trt6-ingestion:dev`

Expected: builds succeed.

- [ ] **Step 6: Commit**

```bash
git add apps/worker-llm/Dockerfile apps/worker-scrapper/Dockerfile apps/ingestion/Dockerfile docker/entrypoints/celery.sh
git commit -m "feat: dockerize workers and ingestion"
```

---

### Task 5: Update Compose for Full E2E

**Files:**
- Modify: `compose.yaml`

- [ ] **Step 1: Add postgres + api + workers + ingestion services**

Modify `compose.yaml` accordingly (include `postgres_data` volume) and ensure:

- API is published `8000:8000`
- `worker-llm` has `extra_hosts: ["host.docker.internal:host-gateway"]`
- All Python services set `CELERY_BROKER_URL=amqp://user:password@rabbitmq:5672//`
- All services set MinIO env vars to `minio:9000` creds.

- [ ] **Step 2: Run `docker compose config` sanity check**

Run: `docker compose config -q`

Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
git add compose.yaml
git commit -m "feat: compose stack for full docker e2e"
```

---

### Task 6: Full E2E Runbook (Manual Validation)

**Files:**
- Create: `docs/pipeline-e2e-docker-runbook.md`

- [ ] **Step 1: Write runbook**

Create `docs/pipeline-e2e-docker-runbook.md`:

```md
# Docker E2E Runbook (TRT6)

## Prereqs
- LM Studio running on host with OpenAI-compatible server at http://localhost:1234/v1

## Start stack
Run: docker compose up -d --build

## Trigger ingestion
Run: docker compose run --rm ingestion

## Validate
- API reachable: http://localhost:8000/api/processos/
- MinIO console: http://localhost:9001 (minioadmin/minioadmin)
  Expect bucket: pje-documents
  Expect objects: <numero>_<grau>.pdf

## Observe logs
- docker compose logs -f api
- docker compose logs -f worker-scrapper
- docker compose logs -f worker-llm
```

- [ ] **Step 2: Commit**

```bash
git add docs/pipeline-e2e-docker-runbook.md
git commit -m "docs: add docker e2e runbook"
```

---

### Task 7: Execute the E2E Validation

**Files:**
- None

- [ ] **Step 1: Bring up stack**

Run: `docker compose up -d --build`

- [ ] **Step 2: Trigger ingestion**

Run: `docker compose run --rm ingestion`

- [ ] **Step 3: Validate pipeline output**

Run:
- `docker compose logs -f worker-scrapper` (look for upload + llm task dispatch)
- `docker compose logs -f worker-llm` (look for "Analise enviada para API")

Then verify pending list:

```bash
curl -sS http://localhost:8000/api/processos/nao_possuem_pdf/
```

Expected: list shrinks as PDFs appear; analyses are persisted in Postgres.
