from celery import Celery

# Use Redis by default
REDIS_URL = "redis://localhost:6379/0"

celery_app = Celery(
    "codeops_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["codeops.worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
