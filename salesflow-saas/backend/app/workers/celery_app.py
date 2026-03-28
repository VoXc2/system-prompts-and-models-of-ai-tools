from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "dealix",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.follow_up_tasks",
        "app.workers.message_tasks",
        "app.workers.notification_tasks",
        "app.workers.ai_agent_tasks",
        "app.workers.sequence_worker",
        "app.workers.appointment_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Riyadh",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "check-pending-followups": {
        "task": "app.workers.follow_up_tasks.process_pending_followups",
        "schedule": 300.0,  # every 5 minutes
    },
    "send-scheduled-messages": {
        "task": "app.workers.message_tasks.send_scheduled_messages",
        "schedule": 60.0,  # every minute
    },
    "daily-report": {
        "task": "app.workers.notification_tasks.send_daily_report",
        "schedule": {
            "hour": 8,
            "minute": 0,
        },
    },
    "ai-discover-leads": {
        "task": "app.workers.ai_agent_tasks.discover_leads",
        "schedule": 3600.0,  # every hour
        "args": ["default", "healthcare", "الرياض", 10],
    },
    "ai-daily-report": {
        "task": "app.workers.ai_agent_tasks.daily_ai_report",
        "schedule": {
            "hour": 20,
            "minute": 0,
        },
        "args": ["default"],
    },
    "process-sequence-steps": {
        "task": "app.workers.sequence_worker.process_sequence_steps",
        "schedule": 60.0,  # every minute
    },
    "send-appointment-reminders": {
        "task": "app.workers.appointment_tasks.send_appointment_reminders",
        "schedule": 900.0,  # every 15 minutes
    },
    "mark-no-shows": {
        "task": "app.workers.appointment_tasks.mark_no_shows",
        "schedule": 1800.0,  # every 30 minutes
    },
}
