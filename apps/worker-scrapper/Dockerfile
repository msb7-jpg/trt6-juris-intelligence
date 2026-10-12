# syntax=docker/dockerfile:1
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Cache de dependências: copia apenas os manifestos do workspace
COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY apps/worker-scrapper/pyproject.toml ./apps/worker-scrapper/

# Instala dependências externas no ambiente virtual /app/.venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --no-dev --package worker-scrapper

# Copia código fonte de shared e worker-scrapper
COPY shared/ ./shared/
COPY apps/worker-scrapper/ ./apps/worker-scrapper/

# Instala os pacotes locais no ambiente virtual
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package worker-scrapper


FROM python:3.13-slim AS runtime

# Dependências de sistema para o Playwright / Chromium
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libnss3 libatk-bridge2.0-0 libxkbcommon0 libxcomposite1 \
        libxrandr2 libxdamage1 libgbm1 libasound2 libxshmfence1 \
        libgtk-3-0 libdrm2 libxfixes3 \
        libxcb1 libx11-6 libxrender1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia o virtualenv pronto e adiciona ao PATH
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Instala o navegador Chromium do Playwright
RUN python -m playwright install chromium

# Copia código da aplicação
COPY --from=builder /app/shared /app/shared
COPY --from=builder /app/apps/worker-scrapper /app/apps/worker-scrapper

COPY docker/entrypoints/celery.sh /entrypoints/celery.sh
RUN chmod +x /entrypoints/celery.sh

ENV APP_MODULE=shared.celery_client
ENV QUEUE=scrapper_queue
ENV INCLUDE=pje_scraper.worker

WORKDIR /app/apps/worker-scrapper

CMD ["/entrypoints/celery.sh"]
