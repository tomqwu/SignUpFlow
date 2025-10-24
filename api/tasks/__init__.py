"""
Background tasks module for asynchronous operations.

Includes:
- SMS notifications via Celery
- Email notifications (future)
- Scheduled reminders
- Batch operations
"""

from api.tasks.sms_tasks import (
    celery_app,
    send_assignment_notification,
    send_event_reminder,
    send_schedule_change_notification,
    send_broadcast_message,
)

__all__ = [
    "celery_app",
    "send_assignment_notification",
    "send_event_reminder",
    "send_schedule_change_notification",
    "send_broadcast_message",
]
