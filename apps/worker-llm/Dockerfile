FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /uvx /bin/

WORKDIR /app

# Workspace-friendly intermediate layers.
# First: install only third-party deps from the root lockfile.
COPY pyproject.toml uv.lock /app/
COPY apps/ingestion/ /app/apps/ingestion/
COPY apps/worker-llm/ /app/apps/worker-llm/
COPY apps/worker-scrapper/ /app/apps/worker-scrapper/
COPY shared/ /app/shared/

RUN uv sync --frozen --no-dev

# Second: copy the full workspace and install workspace members.
COPY shared/ /app/shared/
COPY apps/ingestion/ /app/apps/ingestion/
COPY . /app/
# RUN uv sync --locked --no-dev

# Activate the project venv so entrypoints (e.g. `celery`) resolve.
ENV PATH="/app/.venv/bin:$PATH"

COPY docker/entrypoints/celery.sh /entrypoints/celery.sh
RUN chmod +x /entrypoints/celery.sh

ENV APP_MODULE=shared.celery_client
ENV QUEUE=llm_queue

CMD ["/entrypoints/celery.sh"]
