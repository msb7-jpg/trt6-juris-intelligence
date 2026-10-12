# syntax=docker/dockerfile:1
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Cache de dependências: copia apenas os manifestos do workspace
COPY pyproject.toml uv.lock ./
COPY shared/pyproject.toml ./shared/
COPY apps/api/pyproject.toml ./apps/api/

# Instala dependências externas no ambiente virtual /app/.venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --no-dev --package api

# Copia código fonte de shared e api
COPY shared/ ./shared/
COPY apps/api/ ./apps/api/

# Instala os pacotes locais no ambiente virtual
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package api


FROM python:3.13-slim AS runtime

WORKDIR /app

# Copia o virtualenv pronto e adiciona ao PATH
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copia código da aplicação
COPY --from=builder /app/shared /app/shared
COPY --from=builder /app/apps/api /app/apps/api

COPY docker/entrypoints/api.sh /entrypoints/api.sh
RUN chmod +x /entrypoints/api.sh

WORKDIR /app/apps/api

ENTRYPOINT [ "/entrypoints/api.sh" ]
