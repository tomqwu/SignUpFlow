"""
Notification service for creating and managing email notifications.

Handles notification record creation, email preference checking, and
triggering Celery tasks for sending emails.
"""

import logging
import os
import secrets
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from api.timeutils import utcnow

from api.models import (
    Notification, NotificationType, NotificationStatus,
    EmailPreference, EmailFrequency,
    Person, Assignment
)
from api.tasks.notifications import send_email_task
from api.core.config import settings

logger = logging.getLogger(__name__)
_TRUTHY_VALUES = {"1", "true", "yes", "on"}


def _testing_mode_enabled() -> bool:
    """Return True when the service is running under a test harness."""
    env_flag = os.getenv("TESTING")
    return settings.TESTING or (env_flag is not None and env_flag.lower() in _TRUTHY_VALUES)


def _should_queue_email(send_immediately: bool) -> bool:
    """Centralised gate for deciding whether to enqueue email tasks."""
    if not send_immediately:
        return False
    if _testing_mode_enabled():
        logger.debug("Notification emails suppressed: testing mode active.")
        return False
    if not settings.EMAIL_ENABLED:
        logger.debug("Notification emails suppressed: EMAIL_ENABLED is false.")
        return False
    return True


def create_assignment_notifications(
    assignment_ids: List[int],
    db: Session,
    send_immediately: bool = True
) -> Dict[str, Any]:
    """
    Create notification records for new assignments and optionally send emails.

    Args:
        assignment_ids: List of Assignment IDs to create notifications for
        db: Database session
        send_immediately: If True, queue emails for immediate sending (default: True)

    Returns:
        Dictionary with counts of notifications created and queued

    Example:
        >>> create_assignment_notifications([1, 2, 3], db)
        {'created': 3, 'queued': 2, 'skipped': 1}
    """
    created_count = 0
    queued_count = 0
    skipped_count = 0

    queue_emails = _should_queue_email(send_immediately) and settings.EMAIL_SEND_ASSIGNMENT_NOTIFICATIONS
    logger.debug(
        "create_assignment_notifications queue_emails=%s send_immediately=%s",
        queue_emails,
        send_immediately,
    )

    for assignment_id in assignment_ids:
        # Get assignment details
        assignment = db.query(Assignment).filter(
            Assignment.id == assignment_id
        ).first()

        if not assignment:
            logger.warning(f"Assignment {assignment_id} not found")
            skipped_count += 1
            continue

        # Get person
        person = db.query(Person).filter(
            Person.id == assignment.person_id
        ).first()

        if not person:
            logger.warning(f"Person {assignment.person_id} not found")
            skipped_count += 1
            continue

        # Get or create email preferences
        email_pref = db.query(EmailPreference).filter(
            EmailPreference.person_id == person.id
        ).first()

        if not email_pref:
            # Create default email preferences with unsubscribe token
            email_pref = EmailPreference(
                person_id=person.id,
                org_id=person.org_id,
                frequency=EmailFrequency.IMMEDIATE,
                enabled_types=[
                    NotificationType.ASSIGNMENT,
                    NotificationType.REMINDER,
                    NotificationType.UPDATE,
                    NotificationType.CANCELLATION
                ],
                language=person.language if hasattr(person, 'language') and person.language else "en",
                timezone=person.timezone if hasattr(person, 'timezone') and person.timezone else "UTC",
                unsubscribe_token=secrets.token_urlsafe(32)
            )
            db.add(email_pref)
            db.flush()

        # Check if assignment notifications are enabled
        if NotificationType.ASSIGNMENT not in (email_pref.enabled_types or []):
            logger.info(f"Assignment notifications disabled for person {person.id}")
            skipped_count += 1
            continue

        # Create notification record
        notification = Notification(
            org_id=person.org_id,
            recipient_id=person.id,
            type=NotificationType.ASSIGNMENT,
            status=NotificationStatus.PENDING,
            event_id=assignment.event_id,
            template_data={
                "assignment_id": assignment.id,
                "role": assignment.role if hasattr(assignment, 'role') else None,
            },
            created_at=utcnow()
        )
        db.add(notification)
        db.flush()  # Flush to get notification ID

        created_count += 1

        # Queue email if immediate frequency
        if queue_emails and email_pref.frequency == EmailFrequency.IMMEDIATE:
            try:
                send_email_task.delay(notification.id)
                queued_count += 1
                logger.info(f"Queued email for notification {notification.id}")
            except Exception as e:
                logger.error(f"Failed to queue email for notification {notification.id}: {e}")

    # Commit all changes
    db.commit()

    logger.info(
        f"Assignment notifications: {created_count} created, "
        f"{queued_count} queued, {skipped_count} skipped"
    )

    return {
        "created": created_count,
        "queued": queued_count,
        "skipped": skipped_count
    }


def create_notification(
    recipient_id: str,
    org_id: str,
    notification_type: str,
    event_id: Optional[str] = None,
    template_data: Optional[Dict[str, Any]] = None,
    db: Session = None,
    send_immediately: bool = True
) -> Optional[Notification]:
    """
    Create a single notification record.

    Args:
        recipient_id: Person ID receiving notification
        org_id: Organization ID
        notification_type: Type of notification (from NotificationType)
        event_id: Related event ID (optional)
        template_data: Template rendering data (optional)
        db: Database session
        send_immediately: Queue for immediate sending if user has immediate frequency

    Returns:
        Created Notification instance or None if skipped

    Example:
        >>> notification = create_notification(
        ...     recipient_id="person_123",
        ...     org_id="org_456",
        ...     notification_type=NotificationType.REMINDER,
        ...     event_id="event_789",
        ...     db=db
        ... )
    """
    # Get email preferences
    email_pref = db.query(EmailPreference).filter(
        EmailPreference.person_id == recipient_id
    ).first()

    # Check if notification type is enabled
    if email_pref and notification_type not in (email_pref.enabled_types or []):
        logger.info(f"{notification_type} notifications disabled for person {recipient_id}")
        return None

    # Create notification
    notification = Notification(
        org_id=org_id,
        recipient_id=recipient_id,
        type=notification_type,
        status=NotificationStatus.PENDING,
        event_id=event_id,
        template_data=template_data or {},
        created_at=utcnow()
    )
    db.add(notification)
    db.flush()

    queue_emails = _should_queue_email(send_immediately) and settings.EMAIL_SEND_UPDATE_NOTIFICATIONS

    # Queue email if immediate frequency
    if queue_emails and (not email_pref or email_pref.frequency == EmailFrequency.IMMEDIATE):
        try:
            send_email_task.delay(notification.id)
            logger.info(f"Queued email for notification {notification.id}")
        except Exception as e:
            logger.error(f"Failed to queue email for notification {notification.id}: {e}")

    return notification


def get_pending_notifications_for_digest(
    person_id: str,
    frequency: str,
    db: Session
) -> List[Notification]:
    """
    Get pending notifications for daily/weekly digest.

    Args:
        person_id: Person ID
        frequency: EmailFrequency (DAILY or WEEKLY)
        db: Database session

    Returns:
        List of pending Notification records

    Example:
        >>> notifications = get_pending_notifications_for_digest(
        ...     person_id="person_123",
        ...     frequency=EmailFrequency.DAILY,
        ...     db=db
        ... )
    """
    return db.query(Notification).filter(
        Notification.recipient_id == person_id,
        Notification.status == NotificationStatus.PENDING,
        Notification.type.in_([
            NotificationType.ASSIGNMENT,
            NotificationType.UPDATE,
            NotificationType.CANCELLATION
        ])
    ).all()
