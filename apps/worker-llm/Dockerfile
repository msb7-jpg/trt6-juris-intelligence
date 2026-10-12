# syntax=docker/dockerfile:1
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Cache de dependências: copia apenas os manifestos do workspace
COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY apps/worker-llm/pyproject.toml ./apps/worker-llm/

# Instala dependências externas no ambiente virtual /app/.venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --no-dev --package worker-llm

# Copia código fonte de shared e worker-llm
COPY shared/ ./shared/
COPY apps/worker-llm/ ./apps/worker-llm/

# Instala os pacotes locais no ambiente virtual
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package worker-llm


FROM python:3.13-slim AS runtime

# JRE headless requerido pelo opendataloader-pdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jre-headless && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Copia o virtualenv pronto e adiciona ao PATH
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copia código da aplicação
COPY --from=builder /app/shared /app/shared
COPY --from=builder /app/apps/worker-llm /app/apps/worker-llm

COPY docker/entrypoints/celery.sh /entrypoints/celery.sh
RUN chmod +x /entrypoints/celery.sh

ENV APP_MODULE=shared.celery_client
ENV QUEUE=llm_queue
ENV INCLUDE=worker
ENV CELERY_ARGS=--concurrency=1

WORKDIR /app/apps/worker-llm

CMD ["/entrypoints/celery.sh"]
