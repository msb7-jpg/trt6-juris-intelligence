FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /uvx /bin/

# System deps for Playwright
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libnss3 libatk-bridge2.0-0 libxkbcommon0 libxcomposite1 \
        libxrandr2 libxdamage1 libgbm1 libasound2 libxshmfence1 \
        libgtk-3-0 libdrm2 libxfixes3 \
        libxcb1 libx11-6 libxrender1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Ensure binaries installed by pip --system are in PATH
ENV PATH="/usr/local/bin:$PATH"

# Copy workspace configuration and needed members
COPY pyproject.toml uv.lock /app/
COPY shared/ /app/shared/
COPY apps/worker-scrapper/ /app/apps/worker-scrapper/

# Export requirements and isolate local workspace packages
RUN uv export --package worker-scrapper --no-dev --no-editable > requirements.txt && \
    awk '/^\.\//{print $1}' requirements.txt > local-packages.txt && \
    grep -v '^\./' requirements.txt > external-requirements.txt

# Build wheels for local packages
RUN mkdir /wheels && \
    if [ -s local-packages.txt ]; then \
        while read -r pkg; do uv build --wheel --out-dir /wheels "$pkg"; done < local-packages.txt; \
    fi

# Install external dependencies globally
RUN uv pip install --system -r external-requirements.txt

# Install local wheels
RUN if [ -d /wheels ] && [ "$(ls -A /wheels)" ]; then \
        uv pip install --system /wheels/*.whl; \
    fi

# Playwright browsers
RUN python -m playwright install --with-deps chromium

# Verify installation
RUN python -c "import shared; print('Success: shared module installed')"

# Finalize app setup
WORKDIR /app/apps/worker-scrapper

COPY docker/entrypoints/celery.sh /entrypoints/celery.sh
RUN chmod +x /entrypoints/celery.sh

ENV APP_MODULE=shared.celery_client
ENV QUEUE=scrapper_queue

CMD ["/entrypoints/celery.sh"]
