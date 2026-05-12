# UV Workspace Migration & Optimization Guide

This document summarizes the best practices and technical insights learned from the community guide ["Journey migrating to uv workspace"](https://dev.to/jimmyyeung/journey-migrating-to-uv-workspace-34a7) and applied to this repository.

## 1. Virtual Root Strategy
**Insight**: A monorepo root should act as a coordinator, not a package.
*   **Configuration**: Set `tool.uv.package = false` in the root `pyproject.toml`.
*   **Why**: This prevents `uv` from trying to build/install the root directory itself. It also allows removing workspace members from the root `dependencies` array, preventing environment bloat. Local dev still works seamlessly because `uv sync` resolves the entire workspace tree.

## 2. Resolving the "Editable Install" Trap in Docker
**The Problem**: By default, `uv sync` or `uv pip install -e .` creates `.pth` files pointing to source directories. In multi-stage Docker builds, these source directories are often discarded or moved, leading to `ModuleNotFoundError` even if the package was "installed".

**The Solution**: Use a wheel-based installation strategy for internal workspace packages.
*   **Step 1: Export**: Generate a `requirements.txt` that includes local paths for workspace members using `uv export --package <app> --no-editable`.
*   **Step 2: Build Wheels**: Filter local paths and build standard Python wheels (`.whl`) using `uv build --wheel`.
*   **Step 3: Install**: Install the wheels into the target environment. This copies the actual code into `site-packages`, making the installation permanent and independent of the original source location.

## 3. Dependency Alignment
**Insight**: `uv` workspaces enforce a single version for any given package across the entire monorepo.
*   **Best Practice**: Audit and align versions (e.g., Django, Pytest, Pydantic) across all apps *before* fully committing to the workspace. This ensures a consistent and conflict-free `uv.lock`.

## 4. Handling Dependency Bloat
**Insight**: Internal libraries often include heavy dependencies that only specific consumers need.
*   **Best Practice**: Use `optional-dependencies` (extras) in internal packages.
*   **Application**: Keep the base `dependencies` minimal for library consumers. Use `[project.optional-dependencies]` for runtime-specific requirements (like `celery` or `django`) that only the service itself needs.

## 5. Optimized Dockerfile Pattern
The following pattern is now used across all services in this repo:

```dockerfile
# 1. Setup uv
COPY --from=ghcr.io/astral-sh/uv /uv /bin/

# 2. Copy workspace config
COPY pyproject.toml uv.lock /app/
COPY shared/ /app/shared/
COPY apps/<name>/ /app/apps/<name>/

# 3. Export & Build Wheels
RUN uv export --package <name> --no-dev --no-editable > requirements.txt && \
    grep '^\./' requirements.txt > local-packages.txt || true && \
    grep -v '^\./' requirements.txt > external-requirements.txt || true

RUN mkdir /wheels && \
    while read -r pkg; do uv build --wheel --out-dir /wheels "$pkg"; done < local-packages.txt

# 4. Permanent Installation
RUN uv pip install --system -r external-requirements.txt && \
    if [ "$(ls -A /wheels)" ]; then uv pip install --system /wheels/*.whl; fi

# 5. Cleanup
RUN rm -rf /app/shared /wheels requirements.txt
```

## Benefits Realized
*   **Reliability**: No more broken path links in production images.
*   **Performance**: Shared caching across the workspace speeds up builds.
*   **Simplicity**: A single source of truth for all dependencies via `uv.lock`.
