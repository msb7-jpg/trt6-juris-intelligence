# Using uv in Docker | uv

> A complete guide to using uv in Docker to manage Python dependencies while optimizing build times and image size via multi-stage builds, intermediate layers, and more.

[Skip to content](https://docs.astral.sh/uv/guides/integration/docker/#using-uv-in-docker)

[![logo](https://docs.astral.sh/uv/assets/logo-letter.svg)](https://docs.astral.sh/uv/)

uv

Using uv in Docker

Type to start searching

[

uv

*   0.11.12
*   84.7k
*   3.1k



](https://github.com/astral-sh/uv)

[![logo](https://docs.astral.sh/uv/assets/logo-letter.svg)](https://docs.astral.sh/uv/)uv

[

uv

](https://github.com/astral-sh/uv)

*   [Introduction](https://docs.astral.sh/uv/)
*   [Getting started](https://docs.astral.sh/uv/getting-started/)
    
    Getting started
    
    *   [Installation](https://docs.astral.sh/uv/getting-started/installation/)
    *   [First steps](https://docs.astral.sh/uv/getting-started/first-steps/)
    *   [Features](https://docs.astral.sh/uv/getting-started/features/)
    *   [Getting help](https://docs.astral.sh/uv/getting-started/help/)
    
*   [Guides](https://docs.astral.sh/uv/guides/)
    
    Guides
    
    *   [Installing Python](https://docs.astral.sh/uv/guides/install-python/)
    *   [Running scripts](https://docs.astral.sh/uv/guides/scripts/)
    *   [Using tools](https://docs.astral.sh/uv/guides/tools/)
    *   [Working on projects](https://docs.astral.sh/uv/guides/projects/)
    *   [Publishing packages](https://docs.astral.sh/uv/guides/package/)
    *   [Migration](https://docs.astral.sh/uv/guides/migration/)
        
        Migration
        
        *   [From pip to a uv project](https://docs.astral.sh/uv/guides/migration/pip-to-project/)
        
    *   [Integrations](https://docs.astral.sh/uv/guides/integration/)
        
        Integrations
        
        *   Docker[Docker](https://docs.astral.sh/uv/guides/integration/docker/)
            
            Table of contents
            
            *   [Getting started](https://docs.astral.sh/uv/guides/integration/docker/#getting-started)
                
                *   [Available images](https://docs.astral.sh/uv/guides/integration/docker/#available-images)
                *   [Installing uv](https://docs.astral.sh/uv/guides/integration/docker/#installing-uv)
                *   [Installing a project](https://docs.astral.sh/uv/guides/integration/docker/#installing-a-project)
                *   [Using the environment](https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment)
                *   [Using installed tools](https://docs.astral.sh/uv/guides/integration/docker/#using-installed-tools)
                
            *   [Developing in a container](https://docs.astral.sh/uv/guides/integration/docker/#developing-in-a-container)
                
                *   [Mounting the project with docker run](https://docs.astral.sh/uv/guides/integration/docker/#mounting-the-project-with-docker-run)
                *   [Configuring watch with docker compose](https://docs.astral.sh/uv/guides/integration/docker/#configuring-watch-with-docker-compose)
                
            *   [Optimizations](https://docs.astral.sh/uv/guides/integration/docker/#optimizations)
                
                *   [Compiling bytecode](https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode)
                *   [Caching](https://docs.astral.sh/uv/guides/integration/docker/#caching)
                *   [Intermediate layers](https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers)
                    
                    *   [Intermediate layers in workspaces](https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers-in-workspaces)
                    
                *   [Non-editable installs](https://docs.astral.sh/uv/guides/integration/docker/#non-editable-installs)
                *   [Using uv temporarily](https://docs.astral.sh/uv/guides/integration/docker/#using-uv-temporarily)
                
            *   [Using the pip interface](https://docs.astral.sh/uv/guides/integration/docker/#using-the-pip-interface)
                
                *   [Installing a package](https://docs.astral.sh/uv/guides/integration/docker/#installing-a-package)
                *   [Installing requirements](https://docs.astral.sh/uv/guides/integration/docker/#installing-requirements)
                *   [Installing a project](https://docs.astral.sh/uv/guides/integration/docker/#installing-a-project_1)
                
            *   [Verifying image provenance](https://docs.astral.sh/uv/guides/integration/docker/#verifying-image-provenance)
            
        *   [Jupyter](https://docs.astral.sh/uv/guides/integration/jupyter/)
        *   [marimo](https://docs.astral.sh/uv/guides/integration/marimo/)
        *   [GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/)
        *   [GitLab CI/CD](https://docs.astral.sh/uv/guides/integration/gitlab/)
        *   [Pre-commit](https://docs.astral.sh/uv/guides/integration/pre-commit/)
        *   [PyTorch](https://docs.astral.sh/uv/guides/integration/pytorch/)
        *   [FastAPI](https://docs.astral.sh/uv/guides/integration/fastapi/)
        *   [Azure Artifacts](https://docs.astral.sh/uv/guides/integration/azure/)
        *   [Google Artifact Registry](https://docs.astral.sh/uv/guides/integration/google/)
        *   [AWS CodeArtifact](https://docs.astral.sh/uv/guides/integration/aws/)
        *   [JFrog Artifactory](https://docs.astral.sh/uv/guides/integration/jfrog/)
        *   [Renovate](https://docs.astral.sh/uv/guides/integration/renovate/)
        *   [Dependabot](https://docs.astral.sh/uv/guides/integration/dependabot/)
        *   [AWS Lambda](https://docs.astral.sh/uv/guides/integration/aws-lambda/)
        *   [Coiled](https://docs.astral.sh/uv/guides/integration/coiled/)
        
    
*   [Concepts](https://docs.astral.sh/uv/concepts/)
    
    Concepts
    
    *   [Projects](https://docs.astral.sh/uv/concepts/projects/)
        
        Projects
        
        *   [Structure and files](https://docs.astral.sh/uv/concepts/projects/layout/)
        *   [Creating projects](https://docs.astral.sh/uv/concepts/projects/init/)
        *   [Managing dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/)
        *   [Running commands](https://docs.astral.sh/uv/concepts/projects/run/)
        *   [Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/)
        *   [Configuring projects](https://docs.astral.sh/uv/concepts/projects/config/)
        *   [Building distributions](https://docs.astral.sh/uv/concepts/projects/build/)
        *   [Exporting lockfiles](https://docs.astral.sh/uv/concepts/projects/export/)
        *   [Using workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/)
        
    *   [Tools](https://docs.astral.sh/uv/concepts/tools/)
    *   [Python versions](https://docs.astral.sh/uv/concepts/python-versions/)
    *   [Configuration files](https://docs.astral.sh/uv/concepts/configuration-files/)
    *   [Package indexes](https://docs.astral.sh/uv/concepts/indexes/)
    *   [Resolution](https://docs.astral.sh/uv/concepts/resolution/)
    *   [Build backend](https://docs.astral.sh/uv/concepts/build-backend/)
    *   [Authentication](https://docs.astral.sh/uv/concepts/authentication/)
        
        Authentication
        
        *   [The auth CLI](https://docs.astral.sh/uv/concepts/authentication/cli/)
        *   [HTTP credentials](https://docs.astral.sh/uv/concepts/authentication/http/)
        *   [Git credentials](https://docs.astral.sh/uv/concepts/authentication/git/)
        *   [TLS certificates](https://docs.astral.sh/uv/concepts/authentication/certificates/)
        *   [Third-party services](https://docs.astral.sh/uv/concepts/authentication/third-party/)
        
    *   [Caching](https://docs.astral.sh/uv/concepts/cache/)
    *   [Preview features](https://docs.astral.sh/uv/concepts/preview/)
    *   [The pip interface](https://docs.astral.sh/uv/pip/)
        
        The pip interface
        
        *   [Using environments](https://docs.astral.sh/uv/pip/environments/)
        *   [Managing packages](https://docs.astral.sh/uv/pip/packages/)
        *   [Inspecting environments](https://docs.astral.sh/uv/pip/inspection/)
        *   [Declaring dependencies](https://docs.astral.sh/uv/pip/dependencies/)
        *   [Locking environments](https://docs.astral.sh/uv/pip/compile/)
        *   [Compatibility with pip](https://docs.astral.sh/uv/pip/compatibility/)
        
    
*   [Reference](https://docs.astral.sh/uv/reference/)
    
    Reference
    
    *   [Commands](https://docs.astral.sh/uv/reference/cli/)
    *   [Settings](https://docs.astral.sh/uv/reference/settings/)
    *   [Environment variables](https://docs.astral.sh/uv/reference/environment/)
    *   [Storage](https://docs.astral.sh/uv/reference/storage/)
    *   [Installer options](https://docs.astral.sh/uv/reference/installer/)
    *   [Troubleshooting](https://docs.astral.sh/uv/reference/troubleshooting/)
        
        Troubleshooting
        
        *   [Build failures](https://docs.astral.sh/uv/reference/troubleshooting/build-failures/)
        *   [Reproducible examples](https://docs.astral.sh/uv/reference/troubleshooting/reproducible-examples/)
        
    *   [Internals](https://docs.astral.sh/uv/reference/internals/)
        
        Internals
        
        *   [Resolver](https://docs.astral.sh/uv/reference/internals/resolver/)
        *   [Workspace Metadata](https://docs.astral.sh/uv/reference/internals/metadata/)
        
    *   [Benchmarks](https://docs.astral.sh/uv/reference/benchmarks/)
    *   [Policies](https://docs.astral.sh/uv/reference/policies/)
        
        Policies
        
        *   [Versioning](https://docs.astral.sh/uv/reference/policies/versioning/)
        *   [Platform support](https://docs.astral.sh/uv/reference/policies/platforms/)
        *   [Python support](https://docs.astral.sh/uv/reference/policies/python/)
        *   [Rust support](https://docs.astral.sh/uv/reference/policies/rust/)
        *   [License](https://docs.astral.sh/uv/reference/policies/license/)
        
    

Table of contents

*   [Getting started](https://docs.astral.sh/uv/guides/integration/docker/#getting-started)
    
    *   [Available images](https://docs.astral.sh/uv/guides/integration/docker/#available-images)
    *   [Installing uv](https://docs.astral.sh/uv/guides/integration/docker/#installing-uv)
    *   [Installing a project](https://docs.astral.sh/uv/guides/integration/docker/#installing-a-project)
    *   [Using the environment](https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment)
    *   [Using installed tools](https://docs.astral.sh/uv/guides/integration/docker/#using-installed-tools)
    
*   [Developing in a container](https://docs.astral.sh/uv/guides/integration/docker/#developing-in-a-container)
    
    *   [Mounting the project with docker run](https://docs.astral.sh/uv/guides/integration/docker/#mounting-the-project-with-docker-run)
    *   [Configuring watch with docker compose](https://docs.astral.sh/uv/guides/integration/docker/#configuring-watch-with-docker-compose)
    
*   [Optimizations](https://docs.astral.sh/uv/guides/integration/docker/#optimizations)
    
    *   [Compiling bytecode](https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode)
    *   [Caching](https://docs.astral.sh/uv/guides/integration/docker/#caching)
    *   [Intermediate layers](https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers)
        
        *   [Intermediate layers in workspaces](https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers-in-workspaces)
        
    *   [Non-editable installs](https://docs.astral.sh/uv/guides/integration/docker/#non-editable-installs)
    *   [Using uv temporarily](https://docs.astral.sh/uv/guides/integration/docker/#using-uv-temporarily)
    
*   [Using the pip interface](https://docs.astral.sh/uv/guides/integration/docker/#using-the-pip-interface)
    
    *   [Installing a package](https://docs.astral.sh/uv/guides/integration/docker/#installing-a-package)
    *   [Installing requirements](https://docs.astral.sh/uv/guides/integration/docker/#installing-requirements)
    *   [Installing a project](https://docs.astral.sh/uv/guides/integration/docker/#installing-a-project_1)
    
*   [Verifying image provenance](https://docs.astral.sh/uv/guides/integration/docker/#verifying-image-provenance)

1.  [Introduction](https://docs.astral.sh/uv/)
2.  [Guides](https://docs.astral.sh/uv/guides/)
3.  [Integrations](https://docs.astral.sh/uv/guides/integration/)

# [Using uv in Docker](https://docs.astral.sh/uv/guides/integration/docker/#using-uv-in-docker)

## [Getting started](https://docs.astral.sh/uv/guides/integration/docker/#getting-started)

Tip

Check out the[`uv-docker-example`](https://github.com/astral-sh/uv-docker-example)project for an example of best practices when using uv to build an application in Docker.

uv provides both_distroless_Docker images, which are useful for[copying uv binaries](https://docs.astral.sh/uv/guides/integration/docker/#installing-uv)into your own image builds, and images derived from popular base images, which are useful for using uv in a container. The distroless images do not contain anything but the uv binaries. In contrast, the derived images include an operating system with uv pre-installed.

As an example, to run uv in a container using a Debian-based image:

```
$dockerrun--rm-itghcr.io/astral-sh/uv:debianuv--help
```

### [Available images](https://docs.astral.sh/uv/guides/integration/docker/#available-images)

The following distroless images are available:

*   `ghcr.io/astral-sh/uv:latest`
*   `ghcr.io/astral-sh/uv:{major}.{minor}.{patch}`, e.g.,`ghcr.io/astral-sh/uv:0.11.12`
*   `ghcr.io/astral-sh/uv:{major}.{minor}`, e.g.,`ghcr.io/astral-sh/uv:0.8`(the latest patch version)

And the following derived images are available:

*   Based on`alpine:3.23`:
    *   `ghcr.io/astral-sh/uv:alpine`
    *   `ghcr.io/astral-sh/uv:alpine3.23`
*   Based on`alpine:3.22`:
    *   `ghcr.io/astral-sh/uv:alpine3.22`
*   Based on`debian:trixie-slim`:
    *   `ghcr.io/astral-sh/uv:debian-slim`
    *   `ghcr.io/astral-sh/uv:trixie-slim`
*   Based on`buildpack-deps:trixie`:
    *   `ghcr.io/astral-sh/uv:debian`
    *   `ghcr.io/astral-sh/uv:trixie`
*   Based on`dhi.io/alpine-base:3.23`:
    *   `ghcr.io/astral-sh/uv:alpine-dhi`
    *   `ghcr.io/astral-sh/uv:alpine3.23-dhi`
*   Based on`dhi.io/debian-base:trixie-debian13`:
    *   `ghcr.io/astral-sh/uv:debian-dhi`
    *   `ghcr.io/astral-sh/uv:trixie-dhi`
*   Based on`dhi/python:3.x`:
    *   `ghcr.io/astral-sh/uv:python3.14-dhi`
    *   `ghcr.io/astral-sh/uv:python3.13-dhi`
    *   `ghcr.io/astral-sh/uv:python3.12-dhi`
    *   `ghcr.io/astral-sh/uv:python3.11-dhi`
    *   `ghcr.io/astral-sh/uv:python3.10-dhi`
*   Based on`python3.x-alpine`:
    *   `ghcr.io/astral-sh/uv:python3.14-alpine`
    *   `ghcr.io/astral-sh/uv:python3.14-alpine3.23`
    *   `ghcr.io/astral-sh/uv:python3.13-alpine`
    *   `ghcr.io/astral-sh/uv:python3.13-alpine3.23`
    *   `ghcr.io/astral-sh/uv:python3.12-alpine`
    *   `ghcr.io/astral-sh/uv:python3.12-alpine3.23`
    *   `ghcr.io/astral-sh/uv:python3.11-alpine`
    *   `ghcr.io/astral-sh/uv:python3.11-alpine3.23`
    *   `ghcr.io/astral-sh/uv:python3.10-alpine`
    *   `ghcr.io/astral-sh/uv:python3.10-alpine3.23`
    *   `ghcr.io/astral-sh/uv:python3.9-alpine`
    *   `ghcr.io/astral-sh/uv:python3.9-alpine3.22`
*   Based on`python3.x-trixie`:
    *   `ghcr.io/astral-sh/uv:python3.14-trixie`
    *   `ghcr.io/astral-sh/uv:python3.13-trixie`
    *   `ghcr.io/astral-sh/uv:python3.12-trixie`
    *   `ghcr.io/astral-sh/uv:python3.11-trixie`
    *   `ghcr.io/astral-sh/uv:python3.10-trixie`
    *   `ghcr.io/astral-sh/uv:python3.9-trixie`
*   Based on`python3.x-slim-trixie`:
    *   `ghcr.io/astral-sh/uv:python3.14-trixie-slim`
    *   `ghcr.io/astral-sh/uv:python3.13-trixie-slim`
    *   `ghcr.io/astral-sh/uv:python3.12-trixie-slim`
    *   `ghcr.io/astral-sh/uv:python3.11-trixie-slim`
    *   `ghcr.io/astral-sh/uv:python3.10-trixie-slim`
    *   `ghcr.io/astral-sh/uv:python3.9-trixie-slim`

As with the distroless image, each derived image is published with uv version tags as`ghcr.io/astral-sh/uv:{major}.{minor}.{patch}-{base}`and`ghcr.io/astral-sh/uv:{major}.{minor}-{base}`, e.g.,`ghcr.io/astral-sh/uv:0.11.12-alpine`.

In addition, starting with`0.8`each derived image also sets`UV_TOOL_BIN_DIR`to`/usr/local/bin`to allow`uv tool install`to work as expected with the default user.

For more details, see the[GitHub Container](https://github.com/astral-sh/uv/pkgs/container/uv)page.

### [Installing uv](https://docs.astral.sh/uv/guides/integration/docker/#installing-uv)

Use one of the above images with uv pre-installed or install uv by copying the binary from the official distroless Docker image:

Dockerfile```
FROMpython:3.12-slim-trixieCOPY--from=ghcr.io/astral-sh/uv:latest/uv/uvx/bin/
```

Or, with the installer:

Dockerfile```
FROMpython:3.12-slim-trixie# The installer requires curl (and certificates) to download the release archiveRUNapt-getupdate&&apt-getinstall-y--no-install-recommendscurlca-certificates# Download the latest installerADDhttps://astral.sh/uv/install.sh/uv-installer.sh# Run the installer then remove itRUNsh/uv-installer.sh&&rm/uv-installer.sh# Ensure the installed binary is on the `PATH`ENVPATH="/root/.local/bin/:$PATH"
```

Note this requires`curl`to be available.

In either case, it is best practice to pin to a specific uv version, e.g., with:

```
COPY--from=ghcr.io/astral-sh/uv:0.11.12/uv/uvx/bin/
```

Tip

While the Dockerfile example above pins to a specific tag, it's also possible to pin a specific SHA256. Pinning a specific SHA256 is considered best practice in environments that require reproducible builds as tags can be moved across different commit SHAs.

```
# e.g., using a hash from a previous releaseCOPY--from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709/uv/uvx/bin/
```

Or, with the installer:

```
ADDhttps://astral.sh/uv/0.11.12/install.sh/uv-installer.sh
```

### [Installing a project](https://docs.astral.sh/uv/guides/integration/docker/#installing-a-project)

If you're using uv to manage your project, you can copy it into the image and install it:

Dockerfile```
# Copy the project into the imageCOPY./app# Disable development dependenciesENVUV_NO_DEV=1# Sync the project into a new environment, asserting the lockfile is up to dateWORKDIR/appRUNuvsync--locked
```

Important

It is best practice to add`.venv`to a[`.dockerignore`file](https://docs.docker.com/build/concepts/context/#dockerignore-files)in your repository to prevent it from being included in image builds. The project virtual environment is dependent on your local platform and should be created from scratch in the image.

Then, to start your application by default:

Dockerfile```
# Presuming there is a `my_app` command provided by the projectCMD["uv","run","my_app"]
```

Tip

It is best practice to use[intermediate layers](https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers)separating installation of dependencies and the project itself to improve Docker image build times.

See a complete example in the[`uv-docker-example`project](https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile).

### [Using the environment](https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment)

Once the project is installed, you can either_activate_the project virtual environment by placing its binary directory at the front of the path:

Dockerfile```
ENVPATH="/app/.venv/bin:$PATH"
```

Or, you can use`uv run`for any commands that require the environment:

Dockerfile```
RUNuvrunsome_script.py
```

Tip

Alternatively, the[`UV_PROJECT_ENVIRONMENT`setting](https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path)can be set before syncing to install to the system Python environment and skip environment activation entirely.

### [Using installed tools](https://docs.astral.sh/uv/guides/integration/docker/#using-installed-tools)

To use installed tools, ensure the[tool bin directory](https://docs.astral.sh/uv/concepts/tools/#tool-executables)is on the path:

Dockerfile```
ENVPATH=/root/.local/bin:$PATHRUNuvtoolinstallcowsay
```

```
$dockerrun-it$(dockerbuild-q.)/bin/bash-c"cowsay -t hello"_____| hello |=====\\^__^(oo)\_______(__)\ )\/\||----w ||| ||
```

Note

The tool bin directory's location can be determined by running the`uv tool dir --bin`command in the container.

Alternatively, it can be set to a constant location:

Dockerfile```
ENVUV_TOOL_BIN_DIR=/opt/uv-bin/
```

## [Developing in a container](https://docs.astral.sh/uv/guides/integration/docker/#developing-in-a-container)

When developing, it's useful to mount the project directory into a container. With this setup, changes to the project can be immediately reflected in a containerized service without rebuilding the image. However, it is important_not_to include the project virtual environment (`.venv`) in the mount, because the virtual environment is platform specific and the one built for the image should be kept.

### [Mounting the project with`docker run`](https://docs.astral.sh/uv/guides/integration/docker/#mounting-the-project-with-docker-run)

Bind mount the project (in the working directory) to`/app`while retaining the`.venv`directory with an[anonymous volume](https://docs.docker.com/engine/storage/#volumes):

```
$dockerrun--rm--volume.:/app--volume/app/.venv[...]
```

Tip

The`--rm`flag is included to ensure the container and anonymous volume are cleaned up when the container exits.

See a complete example in the[`uv-docker-example`project](https://github.com/astral-sh/uv-docker-example/blob/main/run.sh).

### [Configuring`watch`with`docker compose`](https://docs.astral.sh/uv/guides/integration/docker/#configuring-watch-with-docker-compose)

When using Docker compose, more sophisticated tooling is available for container development. The[`watch`](https://docs.docker.com/compose/file-watch/#compose-watch-versus-bind-mounts)option allows for greater granularity than is practical with a bind mount and supports triggering updates to the containerized service when files change.

Note

This feature requires Compose 2.22.0 which is bundled with Docker Desktop 4.24.

Configure`watch`in your[Docker compose file](https://docs.docker.com/compose/compose-application-model/#the-compose-file)to mount the project directory without syncing the project virtual environment and to rebuild the image when the configuration changes:

compose.yaml```
services:example:build:.# ...develop:# Create a `watch` configuration to update the app#watch:# Sync the working directory with the `/app` directory in the container-action:syncpath:.target:/app# Exclude the project virtual environmentignore:-.venv/# Rebuild the image on changes to the `pyproject.toml`-action:rebuildpath:./pyproject.toml
```

Then, run`docker compose watch`to run the container with the development setup.

See a complete example in the[`uv-docker-example`project](https://github.com/astral-sh/uv-docker-example/blob/main/compose.yml).

## [Optimizations](https://docs.astral.sh/uv/guides/integration/docker/#optimizations)

### [Compiling bytecode](https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode)

Compiling Python source files to bytecode is typically desirable for production images as it tends to improve startup time (at the cost of increased installation time and image size).

To enable bytecode compilation, use the`--compile-bytecode`flag:

Dockerfile```
RUNuvpythoninstall--compile-bytecodeRUNuvsync--compile-bytecode
```

Alternatively, you can set the`UV_COMPILE_BYTECODE`environment variable to ensure that all commands within the Dockerfile compile bytecode:

Dockerfile```
ENVUV_COMPILE_BYTECODE=1
```

Note

uv will only compile the standard library of_managed_Python versions during`uv python install`. The distributor of unmanaged Python versions decides if the standard library is pre-compiled. For example, the official`python`image will not have a compiled standard library.

### [Caching](https://docs.astral.sh/uv/guides/integration/docker/#caching)

A[cache mount](https://docs.docker.com/build/guide/mounts/#add-a-cache-mount)can be used to improve performance across builds:

Dockerfile```
ENVUV_LINK_MODE=copyRUN--mount=type=cache,target=/root/.cache/uv\uvsync
```

Changing the[`UV_LINK_MODE`](https://docs.astral.sh/uv/reference/settings/#link-mode)silences warnings about not being able to link files since the cache and sync target are on separate file systems.

If you're not mounting the cache, image size can be reduced by using the`--no-cache`flag or setting`UV_NO_CACHE`.

By default, managed Python installations are not cached before being installed. Setting`UV_PYTHON_CACHE_DIR`can be used in combination with a cache mount:

Dockerfile```
ENVUV_PYTHON_CACHE_DIR=/root/.cache/uv/pythonRUN--mount=type=cache,target=/root/.cache/uv\uvpythoninstall
```

Note

The cache directory's location can be determined by running the`uv cache dir`command in the container.

Alternatively, the cache can be set to a constant location:

Dockerfile```
ENVUV_CACHE_DIR=/opt/uv-cache/
```

### [Intermediate layers](https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers)

If you're using uv to manage your project, you can improve build times by moving your transitive dependency installation into its own layer via the`--no-install`options.

`uv sync --no-install-project`will install the dependencies of the project but not the project itself. Since the project changes frequently, but its dependencies are generally static, this can be a big time saver.

Dockerfile```
# Install uvFROMpython:3.12-slimCOPY--from=ghcr.io/astral-sh/uv:latest/uv/uvx/bin/# Change the working directory to the `app` directoryWORKDIR/app# Install dependenciesRUN--mount=type=cache,target=/root/.cache/uv\--mount=type=bind,source=uv.lock,target=uv.lock\--mount=type=bind,source=pyproject.toml,target=pyproject.toml\uvsync--locked--no-install-project# Copy the project into the imageCOPY./app# Sync the projectRUN--mount=type=cache,target=/root/.cache/uv\uvsync--locked
```

Note that the`pyproject.toml`is required to identify the project root and name, but the project_contents_are not copied into the image until the final`uv sync`command.

Tip

If you want to remove additional, specific packages from the sync, use`--no-install-package <name>`.

#### [Intermediate layers in workspaces](https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers-in-workspaces)

If you're using a[workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/), then a couple changes are needed:

*   Use`--frozen`instead of`--locked`during the initially sync.
*   Use the`--no-install-workspace`flag which excludes the project_and_any workspace members.

Dockerfile```
# Install uvFROMpython:3.12-slimCOPY--from=ghcr.io/astral-sh/uv:latest/uv/uvx/bin/WORKDIR/appRUN--mount=type=cache,target=/root/.cache/uv\--mount=type=bind,source=uv.lock,target=uv.lock\--mount=type=bind,source=pyproject.toml,target=pyproject.toml\uvsync--frozen--no-install-workspaceCOPY./appRUN--mount=type=cache,target=/root/.cache/uv\uvsync--locked
```

uv cannot assert that the`uv.lock`file is up-to-date without each of the workspace member`pyproject.toml`files, so we use`--frozen`instead of`--locked`to skip the check during the initial sync. The next sync, after all the workspace members have been copied, can still use`--locked`and will validate that the lockfile is correct for all workspace members.

### [Non-editable installs](https://docs.astral.sh/uv/guides/integration/docker/#non-editable-installs)

By default, uv installs projects and workspace members in editable mode, such that changes to the source code are immediately reflected in the environment.

`uv sync`and`uv run`both accept a`--no-editable`flag, which instructs uv to install the project in non-editable mode, removing any dependency on the source code.

In the context of a multi-stage Docker image,`--no-editable`can be used to include the project in the synced virtual environment from one stage, then copy the virtual environment alone (and not the source code) into the final image.

For example:

Dockerfile```
# Install uvFROMpython:3.12-slimASbuilderCOPY--from=ghcr.io/astral-sh/uv:latest/uv/uvx/bin/# Use the system Python across both stagesENVUV_PYTHON_DOWNLOADS=0# Change the working directory to the `app` directoryWORKDIR/app# Install dependenciesRUN--mount=type=cache,target=/root/.cache/uv\--mount=type=bind,source=uv.lock,target=uv.lock\--mount=type=bind,source=pyproject.toml,target=pyproject.toml\uvsync--locked--no-install-project--no-editable# Copy the project into the intermediate imageCOPY./app# Sync the projectRUN--mount=type=cache,target=/root/.cache/uv\uvsync--locked--no-editableFROMpython:3.12-slim# Copy the environment, but not the source codeCOPY--from=builder/app/.venv/app/.venv# Run the applicationCMD["/app/.venv/bin/hello"]
```

### [Using uv temporarily](https://docs.astral.sh/uv/guides/integration/docker/#using-uv-temporarily)

If uv isn't needed in the final image, the binary can be mounted in each invocation:

Dockerfile```
RUN--mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv\uvsync
```

## [Using the pip interface](https://docs.astral.sh/uv/guides/integration/docker/#using-the-pip-interface)

### [Installing a package](https://docs.astral.sh/uv/guides/integration/docker/#installing-a-package)

The system Python environment is safe to use this context, since a container is already isolated. The`--system`flag can be used to install in the system environment:

Dockerfile```
RUNuvpipinstall--systemruff
```

To use the system Python environment by default, set the`UV_SYSTEM_PYTHON`variable:

Dockerfile```
ENVUV_SYSTEM_PYTHON=1
```

Alternatively, a virtual environment can be created and activated:

Dockerfile```
RUNuvvenv/opt/venv# Use the virtual environment automaticallyENVVIRTUAL_ENV=/opt/venv# Place entry points in the environment at the front of the pathENVPATH="/opt/venv/bin:$PATH"
```

When using a virtual environment, the`--system`flag should be omitted from uv invocations:

Dockerfile```
RUNuvpipinstallruff
```

### [Installing requirements](https://docs.astral.sh/uv/guides/integration/docker/#installing-requirements)

To install requirements files, copy them into the container:

Dockerfile```
COPYrequirements.txt.RUNuvpipinstall-rrequirements.txt
```

### [Installing a project](https://docs.astral.sh/uv/guides/integration/docker/#installing-a-project_1)

When installing a project alongside requirements, it is best practice to separate copying the requirements from the rest of the source code. This allows the dependencies of the project (which do not change often) to be cached separately from the project itself (which changes very frequently).

Dockerfile```
COPYpyproject.toml.RUNuvpipinstall-rpyproject.tomlCOPY..RUNuvpipinstall-e.
```

## [Verifying image provenance](https://docs.astral.sh/uv/guides/integration/docker/#verifying-image-provenance)

The Docker images are signed during the build process to provide proof of their origin. These attestations can be used to verify that an image was produced from an official channel.

For example, you can verify the attestations with the[GitHub CLI tool`gh`](https://cli.github.com/):

```
$ghattestationverify--ownerastral-shoci://ghcr.io/astral-sh/uv:latestLoaded digest sha256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx for oci://ghcr.io/astral-sh/uv:latestLoaded 1 attestation from GitHub APIThe following policy criteria will be enforced:- OIDC Issuer must match:................... https://token.actions.githubusercontent.com- Source Repository Owner URI must match:... https://github.com/astral-sh- Predicate type must match:................ https://slsa.dev/provenance/v1- Subject Alternative Name must match regex: (?i)^https://github.com/astral-sh/✓ Verification succeeded!sha256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx was attested by:REPO PREDICATE_TYPE WORKFLOWastral-sh/uv https://slsa.dev/provenance/v1 .github/workflows/build-docker.yml@refs/heads/main
```

This tells you that the specific Docker image was built by the official uv GitHub release workflow and hasn't been tampered with since.

GitHub attestations build on the[sigstore.dev infrastructure](https://www.sigstore.dev/). As such you can also use the[`cosign`command](https://github.com/sigstore/cosign)to verify the attestation blob against the (multi-platform) manifest for`uv`:

```
$REPO=astral-sh/uv$ghattestationdownload--repo$REPOoci://ghcr.io/${REPO}:latestWrote attestations to file sha256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.jsonl.Any previous content has been overwrittenThe trusted metadata is now available at sha256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.jsonl$dockerbuildximagetoolsinspectghcr.io/${REPO}:latest--format"{{json .Manifest}}">manifest.json$cosignverify-blob-attestation\--new-bundle-format\--bundle"$(jq-r.digestmanifest.json).jsonl"\--certificate-oidc-issuer="https://token.actions.githubusercontent.com"\--certificate-identity-regexp="^https://github\.com/${REPO}/.*"\<(jq-j'.|del(.digest,.size)'manifest.json)Verified OK
```

Tip

These examples use`latest`, but best practice is to verify the attestation for a specific version tag, e.g.,`ghcr.io/astral-sh/uv:0.11.12`, or (even better) the specific image digest, such as`ghcr.io/astral-sh/uv:0.5.27@sha256:5adf09a5a526f380237408032a9308000d14d5947eafa687ad6c6a2476787b4f`.

May 8, 2026

Back to top

[

Previous

Integration guides



](https://docs.astral.sh/uv/guides/integration/)[

Next

Jupyter

](https://docs.astral.sh/uv/guides/integration/jupyter/)

Made with[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)

[](https://github.com/astral-sh/uv)[](https://discord.com/invite/astral-sh)[](https://pypi.org/project/uv/)[](https://x.com/astral_sh)

Human readable version: https://docs.astral.sh/uv/guides/integration/docker/#verifying-image-provenance