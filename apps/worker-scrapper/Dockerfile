FROM python:3.13-slim

# Pull uv binary
COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /uvx /bin/

ENV PYTHONPATH="/app/shared/src:${PYTHONPATH}"

# System deps for Playwright
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libnss3 libatk-bridge2.0-0 libxkbcommon0 libxcomposite1 \
        libxrandr2 libxdamage1 libgbm1 libasound2 libxshmfence1 \
        libgtk-3-0 libdrm2 libxfixes3 && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY . /app/

RUN uv sync --frozen --no-dev

# Playwright browsers
RUN uv run python -m playwright install --with-deps chromium

# Celery entrypoint
COPY docker/entrypoints/celery.sh /entrypoints/celery.sh
RUN chmod +x /entrypoints/celery.sh

ENV APP_MODULE=shared.celery_client
ENV QUEUE=scrapper_queue

CMD ["/entrypoints/celery.sh"]
