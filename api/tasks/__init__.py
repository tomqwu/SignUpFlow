"""
Background tasks module for asynchronous operations.

Includes:
- SMS notifications via Celery
- Billing and subscription tasks
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

from api.tasks.billing_tasks import (
    check_expired_trials,
    send_trial_expiration_warning,
    check_usage_limits,
)

__all__ = [
    "celery_app",
    "send_assignment_notification",
    "send_event_reminder",
    "send_schedule_change_notification",
    "send_broadcast_message",
    "check_expired_trials",
    "send_trial_expiration_warning",
    "check_usage_limits",
]
