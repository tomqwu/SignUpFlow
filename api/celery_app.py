"""
Celery application for asynchronous email notification tasks.

This module initializes the Celery app and configures scheduled tasks (Celery Beat).
"""

from typing import Any

from celery import Celery, signals
from celery.schedules import crontab

from api.core.config import settings
from api.core.runtime_config import validate_production_environment

# Initialize Celery app
celery_app = Celery(
    "signupflow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["api.tasks.notifications"],
)

# Celery configuration
celery_app.conf.update(
    # Task result expiration (7 days)
    result_expires=604800,
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task execution settings
    task_acks_late=True,  # Acknowledge tasks after execution (not before)
    task_reject_on_worker_lost=True,  # Re-queue if worker dies
    task_track_started=True,  # Track when tasks start
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    # Worker settings
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
)


@signals.worker_init.connect  # type: ignore[misc]
@signals.beat_init.connect  # type: ignore[misc]
def validate_celery_production_environment(**_: Any) -> None:
    """Reject unsafe production settings before a worker or beat starts."""
    validate_production_environment()


# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Recover committed notification intents after transient broker outages.
    "dispatch-due-notifications": {
        "task": "api.tasks.notifications.dispatch_due_notifications",
        "schedule": 60.0,
    },
    # Send reminder emails every hour (checks for events 24 hours away)
    "send-reminder-emails": {
        "task": "api.tasks.notifications.send_reminder_emails",
        "schedule": crontab(minute=0),  # Every hour at minute 0
    },
    # Send daily digest emails at 8 AM UTC
    "send-daily-digests": {
        "task": "api.tasks.notifications.send_daily_digests",
        "schedule": crontab(hour=8, minute=0),  # Daily at 8:00 AM UTC
    },
    # Send weekly digest emails on Monday at 8 AM UTC
    "send-weekly-digests": {
        "task": "api.tasks.notifications.send_weekly_digests",
        "schedule": crontab(day_of_week=1, hour=8, minute=0),  # Monday 8:00 AM UTC
    },
    # Send admin summary emails on Monday at 9 AM UTC
    "send-admin-summaries": {
        "task": "api.tasks.notifications.send_admin_summaries",
        "schedule": crontab(day_of_week=1, hour=9, minute=0),  # Monday 9:00 AM UTC
    },
}
