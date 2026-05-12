#!/usr/bin/env bash

# Common entrypoint for Celery workers
# This script sets up the environment and starts the Celery worker.
# It expects the following environment variables to be set:
#   CELERY_APP   - the Python module containing the Celery app (e.g., myproject.celery)
#   CELERY_CMD   - the command to run (default: worker)
#   CELERY_ARGS  - additional arguments for the Celery command

set -euo pipefail

CELERY_APP=${APP_MODULE}

CMD="${CELERY_CMD:-worker}"
ARGS="${CELERY_ARGS:-}"

exec celery -A "$CELERY_APP" "$CMD" $ARGS
