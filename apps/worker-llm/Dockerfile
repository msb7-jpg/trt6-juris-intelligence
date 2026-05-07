FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /uvx /bin/

ENV PYTHONPATH="/app/shared/src:${PYTHONPATH}"

COPY . /app/

RUN uv sync --frozen --no-dev

COPY docker/entrypoints/celery.sh /entrypoints/celery.sh
RUN chmod +x /entrypoints/celery.sh

ENV APP_MODULE=shared.celery_client
ENV QUEUE=llm_queue

CMD ["/entrypoints/celery.sh"]
