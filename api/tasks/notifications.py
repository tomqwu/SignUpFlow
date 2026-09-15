"""
Celery tasks for email notifications.

Background tasks for sending assignment notifications, reminders, digests,
and admin summaries asynchronously.
"""

import logging
import uuid
from datetime import timedelta
from typing import Any, cast

from sqlalchemy.orm import Session

from api.celery_app import celery_app
from api.database import get_db
from api.models import (
    Assignment,
    EmailFrequency,
    EmailPreference,
    Event,
    Notification,
    NotificationStatus,
    NotificationType,
    Organization,
    Person,
)
from api.services.email_service import email_service
from api.services.notification_outbox import (
    claim_notification,
    complete_notification,
    defer_notification_to_digest,
    due_notification_refs,
    fail_notification,
    mark_notification_uncertain,
    suppress_notification,
)
from api.timeutils import utcnow

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=0)  # type: ignore[misc]
def send_email_task(self: Any, notification_id: int, org_id: str) -> dict[str, Any]:
    """
    Send single email notification asynchronously.

    This task retrieves a Notification from the database, sends the email,
    and updates the notification status.

    Args:
        notification_id: ID of Notification to send
        org_id: Tenant owning the intent.

    Returns:
        Dictionary with status and message_id

    Example:
        >>> send_email_task.delay(notification_id=123, org_id="org_456")
    """
    db: Session = next(get_db())
    lease_token = self.request.id or uuid.uuid4().hex
    message_id: str | None = None

    try:
        lookup = db.query(
            Notification.org_id,
            Notification.status,
            Notification.sendgrid_message_id,
        ).filter(Notification.id == notification_id, Notification.org_id == org_id)
        existing = lookup.one_or_none()
        if existing is None:
            return {"status": "not_due"}
        if existing[1] in {
            NotificationStatus.SENT,
            NotificationStatus.DELIVERED,
            NotificationStatus.OPENED,
            NotificationStatus.CLICKED,
        }:
            return {"status": "already_sent", "message_id": existing[2]}
        if email_service.delivery_mode == "disabled":
            return {"status": "disabled"}
        notification = claim_notification(
            db,
            notification_id=notification_id,
            org_id=org_id,
            lease_token=lease_token,
        )
        if notification is None:
            return {"status": "not_due"}

        recipient = (
            db.query(Person)
            .filter(Person.id == notification.recipient_id, Person.org_id == org_id)
            .first()
        )

        if not recipient:
            fail_notification(
                db,
                notification_id=notification_id,
                org_id=org_id,
                lease_token=lease_token,
                error="Recipient not found in notification tenant",
                max_attempts=1,
            )
            return {"status": "error", "message": "Recipient not found"}

        email_pref = (
            db.query(EmailPreference)
            .filter(EmailPreference.person_id == recipient.id, EmailPreference.org_id == org_id)
            .first()
        )
        if email_pref and (
            email_pref.frequency == EmailFrequency.DISABLED
            or notification.type not in (email_pref.enabled_types or [])
        ):
            suppress_notification(
                db,
                notification_id=notification_id,
                org_id=org_id,
                lease_token=lease_token,
                reason="Recipient email preference disabled this notification type",
            )
            return {"status": "suppressed"}
        if email_pref and email_pref.frequency in {
            EmailFrequency.DAILY,
            EmailFrequency.WEEKLY,
        }:
            defer_notification_to_digest(
                db,
                notification_id=notification_id,
                org_id=org_id,
                lease_token=lease_token,
            )
            return {"status": "deferred_to_digest"}

        language = cast(str, email_pref.language if email_pref else recipient.language or "en")

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
            fail_notification(
                db,
                notification_id=notification_id,
                org_id=org_id,
                lease_token=lease_token,
                error=f"Unknown notification type: {notification.type}",
                max_attempts=1,
            )
            return {"status": "error", "message": "Unknown notification type"}

        if message_id:
            complete_notification(
                db,
                notification_id=notification_id,
                org_id=org_id,
                lease_token=lease_token,
                message_id=message_id,
            )
            logger.info("Notification %s delivered to configured backend", notification_id)
            return {"status": "success", "message_id": message_id}
        fail_notification(
            db,
            notification_id=notification_id,
            org_id=org_id,
            lease_token=lease_token,
            error="Email delivery backend returned no message identifier",
        )
        logger.error("Email send failed for notification %s", notification_id)
        return {"status": "error", "message": "Email send failed"}

    except Exception as e:
        logger.exception("Error sending notification %s", notification_id)
        db.rollback()
        try:
            if message_id:
                mark_notification_uncertain(
                    db,
                    notification_id=notification_id,
                    org_id=org_id,
                    lease_token=lease_token,
                    error="Provider accepted delivery but local completion was not confirmed",
                )
            else:
                fail_notification(
                    db,
                    notification_id=notification_id,
                    org_id=org_id,
                    lease_token=lease_token,
                    error=str(e),
                )
        except Exception:
            logger.exception("Failed to persist notification delivery failure")
        if message_id:
            return {"status": "uncertain", "message": "Provider outcome requires reconciliation"}
        return {"status": "error", "message": "Delivery failed and remains recoverable"}

    finally:
        db.close()


@celery_app.task  # type: ignore[misc]
def dispatch_due_notifications(limit_per_org: int = 100) -> dict[str, Any]:
    """Re-enqueue committed pending/retry intents after broker recovery."""
    if email_service.delivery_mode == "disabled":
        return {"due": 0, "queued": 0, "unavailable": 0, "delivery": "disabled"}
    db: Session = next(get_db())
    queued = 0
    unavailable = 0
    try:
        references = due_notification_refs(db, limit_per_org=limit_per_org)
        for notification_id, org_id in references:
            try:
                send_email_task.delay(notification_id, org_id)
            except Exception:
                unavailable += 1
                logger.exception(
                    "Notification broker unavailable; intent remains due",
                    extra={"notification_id": notification_id, "org_id": org_id},
                )
            else:
                queued += 1
        return {"due": len(references), "queued": queued, "unavailable": unavailable}
    finally:
        db.close()


def _send_assignment_notification(
    notification: Notification,
    recipient: Person,
    email_pref: EmailPreference | None,
    language: str,
    db: Session,
) -> str | None:
    """Send assignment notification email."""
    # Get event details
    event = (
        db.query(Event)
        .filter(Event.id == notification.event_id, Event.org_id == notification.org_id)
        .first()
    )
    if not event:
        logger.error(f"Event {notification.event_id} not found")
        return None

    # Get assignment details
    assignment = (
        db.query(Assignment)
        .join(Event, Event.id == Assignment.event_id)
        .filter(
            Assignment.event_id == event.id,
            Assignment.person_id == recipient.id,
            Event.org_id == notification.org_id,
        )
        .first()
    )

    if not assignment:
        logger.error(f"Assignment not found for event {event.id}, person {recipient.id}")
        return None

    # Format event datetime
    event_datetime = event.start_time.strftime("%A, %B %d, %Y at %I:%M %p")

    event_data = cast(dict[str, Any], event.extra_data or {})
    template_data = cast(dict[str, Any], notification.template_data or {})
    unsubscribe_token = cast(str | None, email_pref.unsubscribe_token if email_pref else None)

    # Send email
    return email_service.send_assignment_email(
        volunteer_email=cast(str, recipient.email),
        volunteer_name=cast(str, recipient.name),
        event_title=cast(str, event_data.get("title") or event.type),
        role=cast(str, assignment.role or template_data.get("role", "Volunteer")),
        event_datetime=event_datetime,
        event_location=(
            event_data.get("location") or (event.resource.location if event.resource else None)
        ),
        event_duration=f"{event.duration_minutes} minutes"
        if hasattr(event, "duration_minutes")
        else None,
        additional_info=template_data.get("additional_info"),
        unsubscribe_token=unsubscribe_token,
        notification=notification,
        db=None,
        language=language,
    )


def _send_reminder_notification(
    notification: Notification,
    recipient: Person,
    email_pref: EmailPreference | None,
    language: str,
    db: Session,
) -> str | None:
    """Send reminder notification email."""
    # Get event details
    event = (
        db.query(Event)
        .filter(Event.id == notification.event_id, Event.org_id == notification.org_id)
        .first()
    )
    if not event:
        logger.error(f"Event {notification.event_id} not found")
        return None

    # Get assignment details
    assignment = (
        db.query(Assignment)
        .join(Event, Event.id == Assignment.event_id)
        .filter(
            Assignment.event_id == event.id,
            Assignment.person_id == recipient.id,
            Event.org_id == notification.org_id,
        )
        .first()
    )

    if not assignment:
        logger.error(f"Assignment not found for event {event.id}, person {recipient.id}")
        return None

    # Calculate hours remaining
    now = utcnow()
    hours_remaining = int((event.start_time - now).total_seconds() / 3600)

    # Format event datetime
    event_datetime = event.start_time.strftime("%A, %B %d, %Y at %I:%M %p")

    event_data = cast(dict[str, Any], event.extra_data or {})
    unsubscribe_token = cast(str | None, email_pref.unsubscribe_token if email_pref else None)
    template_data = cast(dict[str, Any], notification.template_data or {})

    # Send email
    return email_service.send_reminder_email(
        volunteer_email=cast(str, recipient.email),
        volunteer_name=cast(str, recipient.name),
        event_title=cast(str, event_data.get("title") or event.type),
        role=cast(str, assignment.role or template_data.get("role", "Volunteer")),
        event_datetime=event_datetime,
        hours_remaining=hours_remaining,
        event_location=(
            event_data.get("location") or (event.resource.location if event.resource else None)
        ),
        event_duration=f"{event.duration_minutes} minutes"
        if hasattr(event, "duration_minutes")
        else None,
        what_to_bring=template_data.get("what_to_bring"),
        additional_info=template_data.get("additional_info"),
        unsubscribe_token=unsubscribe_token,
        notification=notification,
        db=None,
        language=language,
    )


def _send_update_notification(
    notification: Notification,
    recipient: Person,
    email_pref: EmailPreference | None,
    language: str,
    db: Session,
) -> str | None:
    """Send update notification email."""
    # Get event details
    event = (
        db.query(Event)
        .filter(Event.id == notification.event_id, Event.org_id == notification.org_id)
        .first()
    )
    if not event:
        logger.error(f"Event {notification.event_id} not found")
        return None

    # Get assignment details
    assignment = (
        db.query(Assignment)
        .join(Event, Event.id == Assignment.event_id)
        .filter(
            Assignment.event_id == event.id,
            Assignment.person_id == recipient.id,
            Event.org_id == notification.org_id,
        )
        .first()
    )

    if not assignment:
        logger.error(f"Assignment not found for event {event.id}, person {recipient.id}")
        return None

    # Format event datetime
    new_datetime = event.start_time.strftime("%A, %B %d, %Y at %I:%M %p")

    event_data = cast(dict[str, Any], event.extra_data or {})
    unsubscribe_token = cast(str | None, email_pref.unsubscribe_token if email_pref else None)
    template_data = cast(dict[str, Any], notification.template_data or {})
    old_datetime = template_data.get("old_datetime")
    old_location = template_data.get("old_location")
    other_changes = template_data.get("other_changes")

    # Send email
    return email_service.send_update_email(
        volunteer_email=cast(str, recipient.email),
        volunteer_name=cast(str, recipient.name),
        event_title=cast(str, event_data.get("title") or event.type),
        role=cast(str, assignment.role or template_data.get("role", "Volunteer")),
        new_datetime=new_datetime,
        old_datetime=old_datetime,
        new_location=(
            event_data.get("location") or (event.resource.location if event.resource else None)
        ),
        old_location=old_location,
        event_duration=f"{event.duration_minutes} minutes"
        if hasattr(event, "duration_minutes")
        else None,
        other_changes=other_changes,
        unsubscribe_token=unsubscribe_token,
        notification=notification,
        db=None,
        language=language,
    )


def _send_cancellation_notification(
    notification: Notification,
    recipient: Person,
    email_pref: EmailPreference | None,
    language: str,
    db: Session,
) -> str | None:
    """Send cancellation notification email."""
    # Get event details
    event = (
        db.query(Event)
        .filter(Event.id == notification.event_id, Event.org_id == notification.org_id)
        .first()
    )
    if not event:
        logger.error(f"Event {notification.event_id} not found")
        return None

    # Format event datetime
    event_datetime = event.start_time.strftime("%A, %B %d, %Y at %I:%M %p")

    event_data = cast(dict[str, Any], event.extra_data or {})
    unsubscribe_token = cast(str | None, email_pref.unsubscribe_token if email_pref else None)
    template_data = cast(dict[str, Any], notification.template_data or {})
    role = cast(str, template_data.get("role", "Volunteer"))
    cancellation_reason = template_data.get("cancellation_reason")
    apology_message = template_data.get("apology_message")

    # Send email
    return email_service.send_cancellation_email(
        volunteer_email=cast(str, recipient.email),
        volunteer_name=cast(str, recipient.name),
        event_title=cast(str, event_data.get("title") or event.type),
        role=role,
        event_datetime=event_datetime,
        event_location=(
            event_data.get("location") or (event.resource.location if event.resource else None)
        ),
        cancellation_reason=cancellation_reason,
        apology_message=apology_message,
        unsubscribe_token=unsubscribe_token,
        notification=notification,
        db=None,
        language=language,
    )


@celery_app.task  # type: ignore[misc]
def send_reminder_emails() -> dict[str, Any]:
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
    notification_refs: list[tuple[int, str]] = []

    try:
        # Find events happening in 23-25 hours (24-hour window with 1-hour buffer)
        now = utcnow()
        reminder_start = now + timedelta(hours=23)
        reminder_end = now + timedelta(hours=25)

        events: list[Event] = []
        for (org_id,) in db.query(Organization.id).all():
            events.extend(
                db.query(Event)
                .filter(
                    Event.org_id == org_id,
                    Event.start_time >= reminder_start,
                    Event.start_time <= reminder_end,
                )
                .all()
            )

        logger.info(f"Found {len(events)} events in 24-hour reminder window")

        for event in events:
            # Get all assignments for this event
            assignments = (
                db.query(Assignment)
                .join(Event, Event.id == Assignment.event_id)
                .filter(Assignment.event_id == event.id, Event.org_id == event.org_id)
                .all()
            )

            for assignment in assignments:
                # Get volunteer
                person = (
                    db.query(Person)
                    .filter(Person.id == assignment.person_id, Person.org_id == event.org_id)
                    .first()
                )

                if not person:
                    continue

                # Get email preferences
                email_pref = (
                    db.query(EmailPreference)
                    .filter(
                        EmailPreference.person_id == person.id,
                        EmailPreference.org_id == event.org_id,
                    )
                    .first()
                )

                # Check if reminders are enabled
                if email_pref and NotificationType.REMINDER not in (email_pref.enabled_types or []):
                    logger.info(f"Reminders disabled for person {person.id}")
                    continue

                # Check if reminder already sent
                existing = (
                    db.query(Notification)
                    .filter(
                        Notification.recipient_id == person.id,
                        Notification.org_id == event.org_id,
                        Notification.event_id == event.id,
                        Notification.type == NotificationType.REMINDER,
                    )
                    .first()
                )

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
                    delivery_key=f"reminder:{event.id}:{person.id}",
                    template_data={
                        "assignment_id": assignment.id,
                        "role": assignment.role if hasattr(assignment, "role") else None,
                        "hours_remaining": int((event.start_time - now).total_seconds() / 3600),
                    },
                    created_at=utcnow(),
                )
                db.add(notification)
                db.flush()
                reminders_created += 1

                # Queue email if immediate frequency
                if email_service.delivery_mode != "disabled" and (
                    not email_pref or email_pref.frequency == EmailFrequency.IMMEDIATE
                ):
                    notification_refs.append((cast(int, notification.id), cast(str, person.org_id)))

        db.commit()
        for notification_id, org_id in notification_refs:
            try:
                send_email_task.delay(notification_id, org_id)
            except Exception:
                logger.exception("Reminder enqueue failed; committed intent remains due")
            else:
                reminders_queued += 1
        logger.info(f"Reminders: {reminders_created} created, {reminders_queued} queued")
        return {"reminders_sent": reminders_queued, "reminders_created": reminders_created}

    except Exception as e:
        logger.error(f"Error in send_reminder_emails task: {e}")
        db.rollback()
        return {"reminders_sent": 0, "error": str(e)}
    finally:
        db.close()


@celery_app.task  # type: ignore[misc]
def send_daily_digests() -> dict[str, Any]:
    """
    Send daily digest emails to users with daily frequency preference.

    Scheduled task that runs at 8 AM UTC via Celery Beat.

    Returns:
        Dictionary with count of digests sent
    """
    # Placeholder for future implementation
    logger.info("send_daily_digests task executed (not yet implemented)")
    return {"digests_sent": 0}


@celery_app.task  # type: ignore[misc]
def send_weekly_digests() -> dict[str, Any]:
    """
    Send weekly digest emails to users with weekly frequency preference.

    Scheduled task that runs Monday 8 AM UTC via Celery Beat.

    Returns:
        Dictionary with count of digests sent
    """
    # Placeholder for future implementation
    logger.info("send_weekly_digests task executed (not yet implemented)")
    return {"digests_sent": 0}


@celery_app.task  # type: ignore[misc]
def send_admin_summaries() -> dict[str, Any]:
    """
    Send weekly admin summary emails to organization admins.

    Scheduled task that runs Monday 9 AM UTC via Celery Beat.

    Returns:
        Dictionary with count of summaries sent
    """
    # Placeholder for Phase 7 implementation
    logger.info("send_admin_summaries task executed (not yet implemented)")
    return {"summaries_sent": 0}
