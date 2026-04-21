from celery import Celery

from src.config import REDIS_URL


celery_app = Celery(
    "file_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.infrastructure.tasks.workers"],
)
