from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "meeting_assistant_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_routes={
        "app.tasks.transcribe_upload": {"queue": "gpu"},
        "app.tasks.run_live_session": {"queue": "gpu"},
        "app.tasks.enroll_voice": {"queue": "gpu"},
        "app.tasks.run_llm": {"queue": "io"},
    },
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks.gpu_tasks", "app.tasks.io_tasks"])
