import os

from celery import Celery

from shared.constants import WORKER_LLM_TASK_NAME, WORKER_SCRAPPER_TASK_NAME

BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://user:password@rabbitmq:5672//")

app = Celery("tasks", broker=BROKER_URL)

app.conf.task_routes = {
    WORKER_SCRAPPER_TASK_NAME: {"queue": "scrapper_queue"},
    WORKER_LLM_TASK_NAME: {"queue": "llm_queue"},
}
