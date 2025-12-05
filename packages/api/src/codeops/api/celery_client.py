from celery import Celery

# Use Redis by default
REDIS_URL = "redis://localhost:6379/0"

celery_client = Celery(
    "codeops_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)
