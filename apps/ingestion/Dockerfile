FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /uvx /bin/

WORKDIR /app

# Workspace-friendly intermediate layers.
COPY pyproject.toml uv.lock /app/
COPY shared/ /app/shared/

RUN uv sync --frozen --no-dev
# RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/apps/ingestion

CMD ["uv", "run", "ingest", "--provider", "api"]
