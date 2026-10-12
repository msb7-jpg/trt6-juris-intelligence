# syntax=docker/dockerfile:1
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Cache de dependências: copia apenas os manifestos do workspace
COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY apps/search-notifier/pyproject.toml ./apps/search-notifier/

# Instala dependências externas no ambiente virtual /app/.venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --no-dev --package search-notifier

# Copia código fonte de shared e search-notifier
COPY shared/ ./shared/
COPY apps/search-notifier/ ./apps/search-notifier/

# Instala os pacotes locais no ambiente virtual
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package search-notifier


FROM python:3.13-slim AS runtime

WORKDIR /app

# Copia o virtualenv pronto e adiciona ao PATH
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copia código da aplicação
COPY --from=builder /app/shared /app/shared
COPY --from=builder /app/apps/search-notifier /app/apps/search-notifier

# Instala supercronic (cron runner para containers)
ADD --chmod=755 https://github.com/aptible/supercronic/releases/download/v0.2.30/supercronic-linux-amd64 /usr/local/bin/supercronic

# Instala crontab
COPY docker/cron/search_notifier.crontab /etc/cron/search_notifier.crontab

WORKDIR /app/apps/search-notifier

CMD ["supercronic", "/etc/cron/search_notifier.crontab"]
