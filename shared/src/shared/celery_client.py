import os

from celery import Celery

BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://user:password@localhost:5672//")

app = Celery("tasks", broker=BROKER_URL)

# Route tasks to dedicated queues.
app.conf.task_routes = {
    "pje_scraper.worker.run_pipeline": {"queue": "scrapper_queue"},
    "worker_llm.run_pipeline": {"queue": "llm_queue"},
    "pje_scraper.deduplication.run": {"queue": "scrapper_queue"},
}

# Route tasks to dedicated queues.
app.conf.task_routes = {
    "pje_scraper.worker.run_pipeline": {"queue": "scrapper_queue"},
    "worker_llm.run_pipeline": {"queue": "llm_queue"},
}
