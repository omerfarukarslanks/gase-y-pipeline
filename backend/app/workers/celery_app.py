from celery import Celery

from app.config import settings

celery_app = Celery(
    "gasey_pipeline",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Celery Beat schedule
celery_app.conf.beat_schedule = {
    "check-scheduled-publishes": {
        "task": "scheduled_publish",
        "schedule": 60.0,  # Every 60 seconds
    },
    "collect-analytics": {
        "task": "collect_analytics",
        "schedule": 3600.0,  # Every hour
    },
    "refresh-tokens": {
        "task": "refresh_tokens",
        "schedule": 1800.0,  # Every 30 minutes
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.workers"])
