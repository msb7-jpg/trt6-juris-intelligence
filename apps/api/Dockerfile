FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Ensure binaries installed by pip --system are in PATH
ENV PATH="/usr/local/bin:$PATH"

# Copy workspace configuration and needed members
COPY pyproject.toml uv.lock /app/
COPY shared/ /app/shared/
COPY apps/api/ /app/apps/api/

# Export requirements and isolate local workspace packages
RUN uv export --package api --no-dev --no-editable > requirements.txt && \
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

# Verify installation of internal dependencies
RUN python -c "import shared; print('Success: shared module installed')"

# Finalize app setup
WORKDIR /app/apps/api

COPY docker/entrypoints/api.sh /entrypoints/api.sh
RUN chmod +x /entrypoints/api.sh

ENTRYPOINT [ "/entrypoints/api.sh" ]
