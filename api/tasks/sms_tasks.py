"""
Celery tasks for asynchronous SMS sending.

Background tasks for:
- Assignment notifications
- Event reminders
- Schedule change notifications
- Broadcast messages
"""

import os
from typing import Any

from celery import Celery

from api.core.features import disabled_sms_task_result, sms_enabled
from api.database import SessionLocal
from api.models import Assignment, Event, Person
from api.services.sms_service import SMSService

# Initialize Celery
celery_app = Celery(
    "signupflow",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
)


@celery_app.task(bind=True, max_retries=3)
def send_assignment_notification(
    self,
    assignment_id: int,
    event_id: str,
    person_id: str,
    organization_id: str,
    language: str = "en",
) -> dict[str, Any]:
    """
    Send assignment notification SMS to single volunteer.

    Args:
        self: Celery task instance
        assignment_id: Assignment ID
        event_id: Event ID
        person_id: Person ID to notify
        organization_id: Organization ID
        language: Language for message ('en' or 'es')

    Returns:
        Dictionary with status, message_id, and delivery info

    Retries:
        Up to 3 times with exponential backoff
    """
    if not sms_enabled():
        return disabled_sms_task_result()
    db = SessionLocal()

    try:
        # 1. Get event and assignment details
        event = (
            db.query(Event).filter(Event.id == event_id, Event.org_id == organization_id).first()
        )
        if not event:
            raise ValueError(f"Event {event_id} not found")

        assignment = (
            db.query(Assignment)
            .filter(
                Assignment.id == assignment_id,
                Assignment.event_id == event_id,
                Assignment.person_id == person_id,
            )
            .first()
        )
        if not assignment:
            raise ValueError(f"Assignment {assignment_id} not found")

        # 2. Get person to get their name for personalized message
        person = (
            db.query(Person)
            .filter(Person.id == person_id, Person.org_id == organization_id)
            .first()
        )
        if not person:
            raise ValueError(f"Person {person_id} not found")

        sms_service = SMSService()

        # 3. Compose assignment message
        message_text = sms_service.compose_assignment_message(
            db=db, event=event, role=assignment.role or "volunteer", language=language
        )

        # Replace {{volunteer_name}} placeholder with actual name
        message_text = message_text.replace("{{volunteer_name}}", person.name)

        # 4. Send SMS
        result = sms_service.send_sms(
            db=db,
            recipient_id=person_id,
            message_text=message_text,
            message_type="assignment",
            organization_id=organization_id,
            event_id=event_id,
            is_urgent=False,
        )

        return {
            "status": "success",
            "message_id": result["message_id"],
            "phone_number": result["phone_number"],
            "cost_cents": result["cost_cents"],
        }

    except Exception as exc:
        # Retry with exponential backoff: 60s, 300s, 900s
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))

    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def send_event_reminder(
    self,
    event_id: str,
    organization_id: str,
    hours_before: int = 24,
    language: str = "en",
) -> dict[str, Any]:
    """
    Send reminder SMS to all assigned volunteers for an event.

    Args:
        self: Celery task instance
        event_id: Event ID
        organization_id: Organization ID
        hours_before: Hours before event to send reminder (default 24)
        language: Language for message ('en' or 'es')

    Returns:
        Dictionary with total sent, skipped, and cost

    Retries:
        Up to 3 times with exponential backoff
    """
    if not sms_enabled():
        return disabled_sms_task_result()
    db = SessionLocal()

    try:
        # 1. Get event
        event = (
            db.query(Event).filter(Event.id == event_id, Event.org_id == organization_id).first()
        )
        if not event:
            raise ValueError(f"Event {event_id} not found")

        # 2. Get all assignments for this event
        assignments = db.query(Assignment).filter(Assignment.event_id == event_id).all()

        if not assignments:
            return {
                "status": "success",
                "total_sent": 0,
                "message": "No assignments found for event",
            }

        # 3. Get reminder template
        from api.models import SmsTemplate

        template = (
            db.query(SmsTemplate)
            .filter(
                SmsTemplate.organization_id == organization_id,
                SmsTemplate.message_type == "reminder",
                SmsTemplate.is_system is True,
            )
            .first()
        )

        if not template:
            raise ValueError(f"No reminder template found for organization {organization_id}")

        sms_service = SMSService()

        # 4. Build context
        event_datetime = event.start_time
        date_str = event_datetime.strftime("%A, %B %d")
        time_str = event_datetime.strftime("%I:%M %p")

        context = {
            "event_name": (event.extra_data or {}).get("title", event.type),
            "date": date_str,
            "time": time_str,
            "location": (event.extra_data or {}).get("location", "TBD"),
        }

        # 5. Render template
        message_text = sms_service.render_template(
            db=db, template_id=template.id, context=context, language=language
        )

        # 6. Send to all assigned volunteers
        recipient_ids = [assignment.person_id for assignment in assignments]

        result = sms_service.send_broadcast(
            db=db,
            recipient_ids=recipient_ids,
            message_text=message_text,
            organization_id=organization_id,
            is_urgent=False,
        )

        return {
            "status": "success",
            "event_id": event_id,
            "total_recipients": result["total_recipients"],
            "queued_count": result["queued_count"],
            "skipped_count": result["skipped_count"],
            "estimated_cost_cents": result["estimated_cost_cents"],
        }

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))

    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def send_schedule_change_notification(
    self,
    event_id: str,
    organization_id: str,
    change_description: str,
    language: str = "en",
) -> dict[str, Any]:
    """
    Send schedule change notification to affected volunteers.

    Args:
        self: Celery task instance
        event_id: Event ID that changed
        organization_id: Organization ID
        change_description: Description of what changed
        language: Language for message ('en' or 'es')

    Returns:
        Dictionary with send results

    Retries:
        Up to 3 times with exponential backoff
    """
    if not sms_enabled():
        return disabled_sms_task_result()
    db = SessionLocal()

    try:
        # 1. Get event
        event = (
            db.query(Event).filter(Event.id == event_id, Event.org_id == organization_id).first()
        )
        if not event:
            raise ValueError(f"Event {event_id} not found")

        # 2. Get all assignments
        assignments = db.query(Assignment).filter(Assignment.event_id == event_id).all()

        if not assignments:
            return {
                "status": "success",
                "total_sent": 0,
                "message": "No assignments to notify",
            }

        sms_service = SMSService()

        # 3. Compose change notification message
        event_datetime = event.start_time
        date_str = event_datetime.strftime("%A, %B %d")
        time_str = event_datetime.strftime("%I:%M %p")

        message_text = (
            f"SCHEDULE CHANGE: {(event.extra_data or {}).get('title', event.type)}\n"
            f"{change_description}\n"
            f"Updated: {date_str} at {time_str}\n"
            f"Location: {(event.extra_data or {}).get('location', 'TBD')}\n"
            f"Reply YES to confirm or NO if unavailable."
        )

        # 4. Send broadcast
        recipient_ids = [assignment.person_id for assignment in assignments]

        result = sms_service.send_broadcast(
            db=db,
            recipient_ids=recipient_ids,
            message_text=message_text,
            organization_id=organization_id,
            is_urgent=True,  # Schedule changes are urgent
            bypass_quiet_hours=False,  # Still respect quiet hours
        )

        return {
            "status": "success",
            "event_id": event_id,
            "change": change_description,
            "total_recipients": result["total_recipients"],
            "queued_count": result["queued_count"],
            "skipped_count": result["skipped_count"],
        }

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))

    finally:
        db.close()


@celery_app.task
def send_broadcast_message(
    recipient_ids: list[str],
    message_text: str,
    organization_id: str,
    is_urgent: bool = False,
) -> dict[str, Any]:
    """
    Send broadcast message to multiple recipients (admin-initiated).

    Args:
        recipient_ids: List of person IDs
        message_text: Broadcast message
        organization_id: Organization ID
        is_urgent: Whether to bypass rate limits

    Returns:
        Dictionary with broadcast results
    """
    if not sms_enabled():
        return disabled_sms_task_result()
    db = SessionLocal()

    try:
        if not recipient_ids or len(recipient_ids) > 200:
            raise ValueError("Invalid SMS recipient count")
        if len(set(recipient_ids)) != len(recipient_ids):
            raise ValueError("recipient_ids must be unique")
        tenant_recipient_ids = {
            person_id
            for (person_id,) in db.query(Person.id)
            .filter(Person.id.in_(recipient_ids), Person.org_id == organization_id)
            .all()
        }
        if tenant_recipient_ids != set(recipient_ids):
            raise ValueError("One or more SMS recipients were not found")

        sms_service = SMSService()
        result = sms_service.send_broadcast(
            db=db,
            recipient_ids=recipient_ids,
            message_text=message_text,
            organization_id=organization_id,
            is_urgent=is_urgent,
            bypass_quiet_hours=False,
        )

        return {
            "status": "success",
            "total_recipients": result["total_recipients"],
            "queued_count": result["queued_count"],
            "skipped_count": result["skipped_count"],
            "estimated_cost_cents": result["estimated_cost_cents"],
        }

    finally:
        db.close()
