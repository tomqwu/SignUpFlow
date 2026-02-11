"""
Celery tasks for email notifications.

Background tasks for sending assignment notifications, reminders, digests,
and admin summaries asynchronously.
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from api.celery_app import celery_app
from api.database import get_db
from api.models import (
    Notification, NotificationType, NotificationStatus,
    EmailPreference, EmailFrequency,
    Person, Event, Assignment, Organization
)
from api.services.email_service import email_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_email_task(
    self,
    notification_id: int
) -> Dict[str, Any]:
    """
    Send single email notification asynchronously.

    This task retrieves a Notification from the database, sends the email,
    and updates the notification status.

    Args:
        notification_id: ID of Notification to send

    Returns:
        Dictionary with status and message_id

    Example:
        >>> send_email_task.delay(notification_id=123)
    """
    db: Session = next(get_db())

    try:
        # Get notification from database
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()

        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return {"status": "error", "message": "Notification not found"}

        # Get recipient
        recipient = db.query(Person).filter(
            Person.id == notification.recipient_id
        ).first()

        if not recipient:
            logger.error(f"Recipient {notification.recipient_id} not found")
            notification.status = NotificationStatus.FAILED
            notification.error_message = "Recipient not found"
            db.commit()
            return {"status": "error", "message": "Recipient not found"}

        # Get email preferences
        email_pref = db.query(EmailPreference).filter(
            EmailPreference.person_id == recipient.id
        ).first()

        # Determine language
        language = email_pref.language if email_pref else recipient.language or "en"

        # Send based on notification type
        if notification.type == NotificationType.ASSIGNMENT:
            message_id = _send_assignment_notification(
                notification, recipient, email_pref, language, db
            )
        elif notification.type == NotificationType.REMINDER:
            message_id = _send_reminder_notification(
                notification, recipient, email_pref, language, db
            )
        elif notification.type == NotificationType.UPDATE:
            message_id = _send_update_notification(
                notification, recipient, email_pref, language, db
            )
        elif notification.type == NotificationType.CANCELLATION:
            message_id = _send_cancellation_notification(
                notification, recipient, email_pref, language, db
            )
        else:
            logger.warning(f"Unknown notification type: {notification.type}")
            notification.status = NotificationStatus.FAILED
            notification.error_message = f"Unknown type: {notification.type}"
            db.commit()
            return {"status": "error", "message": "Unknown notification type"}

        if message_id:
            logger.info(f"Email sent successfully for notification {notification_id}")
            return {"status": "success", "message_id": message_id}
        else:
            logger.error(f"Email send failed for notification {notification_id}")
            return {"status": "error", "message": "Email send failed"}

    except Exception as e:
        logger.error(f"Error sending notification {notification_id}: {e}")

        # Update notification status
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            if notification:
                notification.status = NotificationStatus.RETRY
                notification.error_message = str(e)
                db.commit()
        except:
            pass

        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    finally:
        db.close()


def _send_assignment_notification(
    notification: Notification,
    recipient: Person,
    email_pref: Optional[EmailPreference],
    language: str,
    db: Session
) -> Optional[str]:
    """Send assignment notification email."""
    # Get event details
    event = db.query(Event).filter(Event.id == notification.event_id).first()
    if not event:
        logger.error(f"Event {notification.event_id} not found")
        return None

    # Get assignment details
    assignment = db.query(Assignment).filter(
        Assignment.event_id == event.id,
        Assignment.person_id == recipient.id
    ).first()

    if not assignment:
        logger.error(f"Assignment not found for event {event.id}, person {recipient.id}")
        return None

    # Get organization
    org = db.query(Organization).filter(Organization.id == event.org_id).first()

    # Format event datetime
    event_datetime = event.start_time.strftime("%A, %B %d, %Y at %I:%M %p")

    # Get unsubscribe token
    unsubscribe_token = email_pref.unsubscribe_token if email_pref else None

    # Send email
    return email_service.send_assignment_email(
        volunteer_email=recipient.email,
        volunteer_name=recipient.name,
        event_title=(event.extra_data or {}).get("title", event.type),
        role=assignment.role,
        event_datetime=event_datetime,
        event_location=((event.extra_data or {}).get("location") or (event.resource.location if event.resource else None)),
        event_duration=f"{event.duration_minutes} minutes" if hasattr(event, 'duration_minutes') else None,
        additional_info=notification.template_data.get("additional_info") if notification.template_data else None,
        unsubscribe_token=unsubscribe_token,
        notification=notification,
        db=db,
        language=language
    )


def _send_reminder_notification(
    notification: Notification,
    recipient: Person,
    email_pref: Optional[EmailPreference],
    language: str,
    db: Session
) -> Optional[str]:
    """Send reminder notification email."""
    # Get event details
    event = db.query(Event).filter(Event.id == notification.event_id).first()
    if not event:
        logger.error(f"Event {notification.event_id} not found")
        return None

    # Get assignment details
    assignment = db.query(Assignment).filter(
        Assignment.event_id == event.id,
        Assignment.person_id == recipient.id
    ).first()

    if not assignment:
        logger.error(f"Assignment not found for event {event.id}, person {recipient.id}")
        return None

    # Calculate hours remaining
    now = datetime.now(UTC).replace(tzinfo=None)
    hours_remaining = int((event.start_time - now).total_seconds() / 3600)

    # Format event datetime
    event_datetime = event.start_time.strftime("%A, %B %d, %Y at %I:%M %p")

    # Get unsubscribe token
    unsubscribe_token = email_pref.unsubscribe_token if email_pref else None

    # Extract additional info from template_data if available
    template_data = notification.template_data or {}

    # Send email
    return email_service.send_reminder_email(
        volunteer_email=recipient.email,
        volunteer_name=recipient.name,
        event_title=(event.extra_data or {}).get("title", event.type),
        role=assignment.role if hasattr(assignment, 'role') else template_data.get("role", "Volunteer"),
        event_datetime=event_datetime,
        hours_remaining=hours_remaining,
        event_location=((event.extra_data or {}).get("location") or (event.resource.location if event.resource else None)),
        event_duration=f"{event.duration_minutes} minutes" if hasattr(event, 'duration_minutes') else None,
        what_to_bring=template_data.get("what_to_bring"),
        additional_info=template_data.get("additional_info"),
        unsubscribe_token=unsubscribe_token,
        notification=notification,
        db=db,
        language=language
    )


def _send_update_notification(
    notification: Notification,
    recipient: Person,
    email_pref: Optional[EmailPreference],
    language: str,
    db: Session
) -> Optional[str]:
    """Send update notification email."""
    # Get event details
    event = db.query(Event).filter(Event.id == notification.event_id).first()
    if not event:
        logger.error(f"Event {notification.event_id} not found")
        return None

    # Get assignment details
    assignment = db.query(Assignment).filter(
        Assignment.event_id == event.id,
        Assignment.person_id == recipient.id
    ).first()

    if not assignment:
        logger.error(f"Assignment not found for event {event.id}, person {recipient.id}")
        return None

    # Format event datetime
    new_datetime = event.start_time.strftime("%A, %B %d, %Y at %I:%M %p")

    # Get unsubscribe token
    unsubscribe_token = email_pref.unsubscribe_token if email_pref else None

    # Extract change details from template_data
    template_data = notification.template_data or {}
    old_datetime = template_data.get("old_datetime")
    old_location = template_data.get("old_location")
    other_changes = template_data.get("other_changes")

    # Send email
    return email_service.send_update_email(
        volunteer_email=recipient.email,
        volunteer_name=recipient.name,
        event_title=(event.extra_data or {}).get("title", event.type),
        role=assignment.role if hasattr(assignment, 'role') else template_data.get("role", "Volunteer"),
        new_datetime=new_datetime,
        old_datetime=old_datetime,
        new_location=((event.extra_data or {}).get("location") or (event.resource.location if event.resource else None)),
        old_location=old_location,
        event_duration=f"{event.duration_minutes} minutes" if hasattr(event, 'duration_minutes') else None,
        other_changes=other_changes,
        unsubscribe_token=unsubscribe_token,
        notification=notification,
        db=db,
        language=language
    )


def _send_cancellation_notification(
    notification: Notification,
    recipient: Person,
    email_pref: Optional[EmailPreference],
    language: str,
    db: Session
) -> Optional[str]:
    """Send cancellation notification email."""
    # Get event details
    event = db.query(Event).filter(Event.id == notification.event_id).first()
    if not event:
        logger.error(f"Event {notification.event_id} not found")
        return None

    # Format event datetime
    event_datetime = event.start_time.strftime("%A, %B %d, %Y at %I:%M %p")

    # Get unsubscribe token
    unsubscribe_token = email_pref.unsubscribe_token if email_pref else None

    # Extract cancellation details from template_data
    template_data = notification.template_data or {}
    role = template_data.get("role", "Volunteer")
    cancellation_reason = template_data.get("cancellation_reason")
    apology_message = template_data.get("apology_message")

    # Send email
    return email_service.send_cancellation_email(
        volunteer_email=recipient.email,
        volunteer_name=recipient.name,
        event_title=(event.extra_data or {}).get("title", event.type),
        role=role,
        event_datetime=event_datetime,
        event_location=((event.extra_data or {}).get("location") or (event.resource.location if event.resource else None)),
        cancellation_reason=cancellation_reason,
        apology_message=apology_message,
        unsubscribe_token=unsubscribe_token,
        notification=notification,
        db=db,
        language=language
    )


@celery_app.task
def send_reminder_emails() -> Dict[str, Any]:
    """
    Send reminder emails for events 24 hours away.

    Scheduled task that runs every hour via Celery Beat.
    Finds events happening in 24 hours and sends reminder emails.

    Returns:
        Dictionary with count of reminders sent

    Example:
        >>> send_reminder_emails.delay()  # Queue task asynchronously
        >>> send_reminder_emails()  # Run immediately for testing
    """
    db: Session = next(get_db())
    reminders_created = 0
    reminders_queued = 0

    try:
        # Find events happening in 23-25 hours (24-hour window with 1-hour buffer)
        now = datetime.now(UTC).replace(tzinfo=None)
        reminder_start = now + timedelta(hours=23)
        reminder_end = now + timedelta(hours=25)

        events = db.query(Event).filter(
            Event.start_time >= reminder_start,
            Event.start_time <= reminder_end
        ).all()

        logger.info(f"Found {len(events)} events in 24-hour reminder window")

        for event in events:
            # Get all assignments for this event
            assignments = db.query(Assignment).filter(
                Assignment.event_id == event.id
            ).all()

            for assignment in assignments:
                # Get volunteer
                person = db.query(Person).filter(
                    Person.id == assignment.person_id
                ).first()

                if not person:
                    continue

                # Get email preferences
                email_pref = db.query(EmailPreference).filter(
                    EmailPreference.person_id == person.id
                ).first()

                # Check if reminders are enabled
                if email_pref and NotificationType.REMINDER not in (email_pref.enabled_types or []):
                    logger.info(f"Reminders disabled for person {person.id}")
                    continue

                # Check if reminder already sent
                existing = db.query(Notification).filter(
                    Notification.recipient_id == person.id,
                    Notification.event_id == event.id,
                    Notification.type == NotificationType.REMINDER
                ).first()

                if existing:
                    logger.info(f"Reminder already sent for event {event.id}, person {person.id}")
                    continue

                # Create reminder notification
                notification = Notification(
                    org_id=person.org_id,
                    recipient_id=person.id,
                    type=NotificationType.REMINDER,
                    status=NotificationStatus.PENDING,
                    event_id=event.id,
                    template_data={
                        "assignment_id": assignment.id,
                        "role": assignment.role if hasattr(assignment, 'role') else None,
                        "hours_remaining": int((event.start_time - now).total_seconds() / 3600)
                    },
                    created_at=datetime.now(UTC).replace(tzinfo=None)
                )
                db.add(notification)
                db.flush()
                reminders_created += 1

                # Queue email if immediate frequency
                if not email_pref or email_pref.frequency == EmailFrequency.IMMEDIATE:
                    try:
                        send_email_task.delay(notification.id)
                        reminders_queued += 1
                        logger.info(f"Queued reminder email for notification {notification.id}")
                    except Exception as e:
                        logger.error(f"Failed to queue reminder email: {e}")

        db.commit()
        logger.info(f"Reminders: {reminders_created} created, {reminders_queued} queued")
        return {"reminders_sent": reminders_queued, "reminders_created": reminders_created}

    except Exception as e:
        logger.error(f"Error in send_reminder_emails task: {e}")
        db.rollback()
        return {"reminders_sent": 0, "error": str(e)}
    finally:
        db.close()


@celery_app.task
def send_daily_digests() -> Dict[str, Any]:
    """
    Send daily digest emails to users with daily frequency preference.

    Scheduled task that runs at 8 AM UTC via Celery Beat.

    Returns:
        Dictionary with count of digests sent
    """
    # Placeholder for future implementation
    logger.info("send_daily_digests task executed (not yet implemented)")
    return {"digests_sent": 0}


@celery_app.task
def send_weekly_digests() -> Dict[str, Any]:
    """
    Send weekly digest emails to users with weekly frequency preference.

    Scheduled task that runs Monday 8 AM UTC via Celery Beat.

    Returns:
        Dictionary with count of digests sent
    """
    # Placeholder for future implementation
    logger.info("send_weekly_digests task executed (not yet implemented)")
    return {"digests_sent": 0}


@celery_app.task
def send_admin_summaries() -> Dict[str, Any]:
    """
    Send weekly admin summary emails to organization admins.

    Scheduled task that runs Monday 9 AM UTC via Celery Beat.

    Returns:
        Dictionary with count of summaries sent
    """
    # Placeholder for Phase 7 implementation
    logger.info("send_admin_summaries task executed (not yet implemented)")
    return {"summaries_sent": 0}
