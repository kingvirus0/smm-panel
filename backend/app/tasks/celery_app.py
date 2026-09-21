from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "smm_panel",
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
    beat_schedule={
        "sync-order-status": {
            "task": "app.tasks.order_tasks.sync_order_status",
            "schedule": 60.0,
        },
        "sync-provider-balances": {
            "task": "app.tasks.provider_tasks.sync_provider_balances",
            "schedule": 3600.0,
        },
    },
)

celery_app.autodiscover_tasks(["app.tasks"])
