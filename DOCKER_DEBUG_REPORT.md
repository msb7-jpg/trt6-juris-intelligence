# Docker Debug Report (worker-llm build)

Date: 2026-05-10

## Summary

1. Initial build failure for `worker-llm` was a Dockerfile working-directory issue: `uv sync` ran outside `/app`, so `uv` could not find `pyproject.toml`.
2. After fixing `WORKDIR`, `uv sync` progressed but build sometimes failed with network/DNS errors when downloading wheels.
3. After further attempts, Docker build started crashing with `SIGBUS` during `uv sync`, and eventually the Docker CLI itself started segfaulting (`docker ps`, `docker compose build`, `docker context ls`).

At the end state, this is no longer an app/container problem only: the local Docker CLI/engine integration is unhealthy.

## Repo Context

This is a monorepo with a workspace `pyproject.toml` at repo root:

`/home/miguel/workspace/projetos6/pyproject.toml`

Workspace members include:

`shared`, `apps/ingestion`, `apps/worker-llm`, `apps/worker-scrapper`, `apps/api`

Each app also has its own `pyproject.toml`, including:

`apps/worker-llm/pyproject.toml`

## What Was Working

1. `apps/worker-llm/pyproject.toml` exists in the repo.
2. Docker was able to build images earlier in the session (at least partially).
3. A direct `docker build` using host networking was able to run `uv sync` successfully at least once:

`docker build --no-cache -f apps/worker-llm/Dockerfile --network=host .`

## What Was Not Working

1. `docker compose -f compose.yaml up -d --build worker-llm` initially failed at `uv sync` with:

`error: No \`pyproject.toml\` found in current directory or any parent directory`

2. After fixing `WORKDIR`, `uv sync` sometimes failed fetching packages with DNS-style errors:

`dns error: failed to lookup address information: Name does not resolve`

3. Later, `docker compose` builds started failing with a hard crash during `uv sync`:

`unexpected fault address SIGBUS: bus error`

4. Finally, Docker CLI commands began segfaulting immediately, even without building:

`docker compose -f compose.yaml build worker-llm` -> `Segmentation fault`

`docker ps` -> segfault (exit 139)

`docker context ls` -> segfault (exit 139)

This indicates a broader Docker Desktop / WSL2 / CLI instability, not just an application dependency issue.

## Affected Services / Containers

1. Primary: `worker-llm` image build.
2. Secondary: other services built from the same repo context and running `uv sync` during build (`api`, `worker-scrapper`, `ingestion`) are likely to show the same `WORKDIR`-related symptom if their Dockerfile runs `uv` outside `/app`.
3. End state: all Docker operations are affected because the `docker` CLI itself is crashing.

## Root Cause 1 (Confirmed): Missing `WORKDIR` Before `uv sync`

Evidence:

1. `apps/worker-llm/Dockerfile` had:

```dockerfile
COPY . /app/
RUN uv sync --frozen --no-dev
```

2. Without `WORKDIR /app`, the default working directory is `/`, so `uv` cannot find `/app/pyproject.toml` by walking parents.

Fix applied:

1. Added `WORKDIR /app` before `RUN uv sync` in:

`apps/worker-llm/Dockerfile`

2. Also added `WORKDIR /app` in:

`apps/worker-scrapper/Dockerfile`

Notes:

1. `apps/ingestion/Dockerfile` and `apps/api/Dockerfile` already had `WORKDIR /app` before `uv sync`.

## Root Cause 2 (Likely Environmental): Network / DNS / Proxy During Build

Evidence from failed builds:

1. `uv` failed to download wheels from `files.pythonhosted.org` with:

`Could not connect, are you offline?`

`dns error: failed to lookup address information: Name does not resolve`

2. Docker daemon info shows proxy config (captured earlier):

`HTTP Proxy: http.docker.internal:3128`

`HTTPS Proxy: http.docker.internal:3128`

3. DNS resolution from a simple Alpine container was successful at that time:

`nslookup files.pythonhosted.org` resolved to Fastly IPs.

Interpretation:

1. The DNS error might be intermittent.
2. It might be buildkit networking or proxy interaction.
3. It might be transient connectivity from the Docker VM (Docker Desktop) rather than from containers started with default settings.

## Root Cause 3 (Unconfirmed, But Strong Signal): Docker CLI / Engine Instability

Evidence:

1. `docker ps` segfaults (exit 139).
2. `docker context ls` segfaults.
3. `docker compose build` segfaults.
4. `/usr/bin/docker` is a symlink to the Docker Desktop CLI tools path:

`/mnt/wsl/docker-desktop/cli-tools/usr/bin/docker`

Interpretation:

1. The failure mode has moved beyond application builds.
2. This points at a broken Docker Desktop integration, corrupted CLI binary, WSL filesystem/mount issues, or resource pressure causing Go binaries to crash.
3. The earlier `SIGBUS` during build is also consistent with filesystem/memory pressure issues.

## Likely Causes To Search For

1. Docker Desktop WSL2 segfault docker cli (exit 139)
2. Docker Desktop buildkit SIGBUS
3. WSL2 Docker Desktop cli-tools "missing section headers" ELF
4. Docker build SIGBUS uv sync
5. Docker Desktop proxy 3128 DNS resolve issues
6. WSL2 Docker Desktop disk full / corrupted overlayfs

## Recommended Next Narrowing Steps

These are intended to separate "repo/Dockerfile" issues from "Docker Desktop/WSL" issues.

1. Verify Docker CLI health:

`docker version`

`docker info`

If these segfault, stop debugging the app build and focus on Docker Desktop/WSL.

2. If Docker CLI is unstable, try the standard recovery sequence:

Restart Docker Desktop.

Run `wsl --shutdown` (from Windows), then reopen the WSL distro.

3. Check Windows disk space (Docker Desktop often stores VM data on the Windows drive).

Host `df -h` showed `C:\` mounted at `/mnt/c` is 100% full at the time of investigation.

4. If Docker CLI works again, rerun only the `worker-llm` build and capture full logs:

`docker compose -f compose.yaml build --no-cache worker-llm`

5. If network errors persist, test build with host networking (diagnostic):

`docker build --no-cache -f apps/worker-llm/Dockerfile --network=host .`

If this consistently works while normal builds fail, the issue is very likely buildkit network/proxy/DNS behavior.
