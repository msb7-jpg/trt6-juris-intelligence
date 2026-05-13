FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /uvx /bin/

# JRE required by opendataloader-pdf (runs a bundled JAR via subprocess)
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jre-headless && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Ensure binaries installed by pip --system are in PATH
ENV PATH="/usr/local/bin:$PATH"

# Copy workspace configuration and needed members
COPY pyproject.toml uv.lock /app/
COPY shared/ /app/shared/
COPY apps/worker-llm/ /app/apps/worker-llm/

# Export requirements and isolate local workspace packages
RUN uv export --package worker-llm --no-dev --no-editable > requirements.txt && \
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

# Verify installation
RUN python -c "import shared; print('Success: shared module installed')"

# Finalize app setup
WORKDIR /app/apps/worker-llm

COPY docker/entrypoints/celery.sh /entrypoints/celery.sh
RUN chmod +x /entrypoints/celery.sh

ENV APP_MODULE=shared.celery_client
ENV QUEUE=llm_queue
ENV INCLUDE=worker

CMD ["/entrypoints/celery.sh"]
