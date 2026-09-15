"""
SMS API endpoints for notifications and preferences management.

Provides endpoints for:
- Sending assignment notifications
- Phone verification
- SMS preference management
- Broadcast messages
- Incoming webhook handling
"""

import os
from urllib.parse import urlsplit

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from twilio.request_validator import RequestValidator

from api.core.features import require_sms_enabled
from api.database import get_db
from api.dependencies import (
    get_current_admin_user,
    get_current_user,
    get_person_in_actor_org,
    verify_self_or_admin,
)
from api.models import Assignment, Event, Person, SmsMessage, SmsPreference
from api.services.sms_service import SMSService
from api.tasks.sms_tasks import (
    send_assignment_notification,
    send_broadcast_message,
    send_event_reminder,
)
from api.timeutils import utcnow

router = APIRouter(
    prefix="/api/sms",
    tags=["sms"],
    dependencies=[Depends(require_sms_enabled)],
)

_DELIVERY_PROGRESS = {
    "accepted": 0,
    "scheduled": 0,
    "queued": 1,
    "sending": 2,
    "sent": 3,
    "delivered": 4,
    "read": 5,
}
_DELIVERY_FAILURES = {"failed", "undelivered", "canceled"}


# ============================================================================
# Request/Response Models
# ============================================================================


class PhoneVerificationRequest(BaseModel):
    """Request to verify phone number format and deliverability."""

    phone_number: str = Field(..., description="Phone number in E.164 format (+12345678900)")


class PhoneVerificationResponse(BaseModel):
    """Response from phone verification."""

    valid: bool
    carrier_type: str
    formatted_number: str
    deliverable: bool
    country_code: str | None = None
    error: str | None = None


class VerificationCodeRequest(BaseModel):
    """Request to generate and send verification code."""

    person_id: str
    phone_number: str = Field(..., description="Phone number in E.164 format")


class VerificationCodeResponse(BaseModel):
    """Response from verification code generation."""

    message: str
    expires_at: str
    phone_number: str


class VerifyCodeRequest(BaseModel):
    """Request to verify SMS code."""

    person_id: str
    code: int = Field(..., description="6-digit verification code", ge=100000, le=999999)


class VerifyCodeResponse(BaseModel):
    """Response from code verification."""

    verified: bool
    message: str
    phone_number: str


class SendAssignmentNotificationRequest(BaseModel):
    """Request to send assignment notification."""

    assignment_id: int
    event_id: str
    person_id: str
    language: str = Field(default="en", description="Language code (en, es, pt, etc.)")


class SendEventReminderRequest(BaseModel):
    """Request to send event reminder to all assigned volunteers."""

    event_id: str
    hours_before: int = Field(default=24, description="Hours before event to send reminder")
    language: str = Field(default="en", description="Language code")


class SendBroadcastRequest(BaseModel):
    """Request to send broadcast message."""

    recipient_ids: list[str] = Field(..., description="List of person IDs (max 200)")
    message_text: str = Field(..., description="Message content (max 1600 chars)", max_length=1600)
    is_urgent: bool = Field(default=False, description="Bypass rate limits if urgent")


class BroadcastResponse(BaseModel):
    """Response from broadcast send."""

    status: str
    total_recipients: int
    queued_count: int
    skipped_count: int
    estimated_cost_cents: int
    message: str


# ============================================================================
# Phone Verification Endpoints
# ============================================================================


@router.post("/verify-phone", response_model=PhoneVerificationResponse)
def verify_phone_number(
    request: PhoneVerificationRequest,
    current_user: Person = Depends(get_current_user),
):
    """
    Verify phone number format and deliverability using Twilio Lookup API.

    Checks:
    - E.164 format validation
    - Carrier type (mobile vs landline)
    - Deliverability status
    """
    sms_service = SMSService()

    try:
        result = sms_service.verify_phone_number(request.phone_number)
        return PhoneVerificationResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phone verification failed: {str(e)}")


@router.post("/send-verification-code", response_model=VerificationCodeResponse)
def send_verification_code(
    request: VerificationCodeRequest,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate and send 6-digit verification code via SMS.

    Code expires in 10 minutes, max 3 verification attempts.
    """
    _authorize_sms_target(request.person_id, current_user, db)

    sms_service = SMSService()

    try:
        sms_service.generate_verification_code(
            db=db, person_id=request.person_id, phone_number=request.phone_number
        )

        from datetime import timedelta

        expires_at = (utcnow() + timedelta(minutes=10)).isoformat()

        return VerificationCodeResponse(
            message="Verification code sent via SMS",
            expires_at=expires_at,
            phone_number=request.phone_number,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send code: {str(e)}")


@router.post("/verify-code", response_model=VerifyCodeResponse)
def verify_code(
    request: VerifyCodeRequest,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify SMS verification code and activate phone for notifications.

    Marks phone as verified and enables SMS notifications.
    """
    _authorize_sms_target(request.person_id, current_user, db)

    sms_service = SMSService()

    try:
        result = sms_service.verify_code(db=db, person_id=request.person_id, code=request.code)
        return VerifyCodeResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


# ============================================================================
# SMS Preferences Management Endpoints
# ============================================================================


class UpdateSmsPreferencesRequest(BaseModel):
    """Request to update SMS notification preferences."""

    notification_types: list[str] = Field(
        ..., description="List of notification types: assignment, reminder, change, cancellation"
    )
    language: str = Field(
        default="en", description="Preferred language for SMS: en, es, pt, zh-CN, zh-TW, fr"
    )


class SmsUsageStatsResponse(BaseModel):
    """Response with SMS usage statistics for organization."""

    month_year: str
    messages_sent: int
    messages_delivered: int
    messages_failed: int
    total_cost_cents: int
    budget_limit_cents: int
    budget_used_percentage: float
    messages_remaining: int | None = None


def _authorize_sms_target(person_id: str, actor: Person, db: Session) -> Person:
    """Resolve a target through the actor's tenant before provider or queue work."""
    target = get_person_in_actor_org(person_id, actor, db)
    verify_self_or_admin(actor, target)
    return target


async def _validated_twilio_form(request: Request, callback_url_env: str) -> dict[str, str]:
    """Validate Twilio's signature against the configured external callback URL."""
    signature = request.headers.get("X-Twilio-Signature")
    if not signature:
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    callback_url = os.getenv(callback_url_env, "").strip()
    parsed_url = urlsplit(callback_url)
    if not auth_token or parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise HTTPException(status_code=503, detail="Twilio callback verification unavailable")
    if (
        os.getenv("ENVIRONMENT", "development").lower() == "production"
        and parsed_url.scheme != "https"
    ):
        raise HTTPException(status_code=503, detail="Twilio callback verification unavailable")

    form_data = await request.form()
    params = {str(key): str(value) for key, value in form_data.multi_items()}
    if not RequestValidator(auth_token).validate(callback_url, params, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")
    return params


@router.put("/people/{person_id}/sms-preferences")
def update_sms_preferences(
    person_id: str,
    request: UpdateSmsPreferencesRequest,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update SMS notification preferences for a user.

    Users can update their own preferences, admins can update any user.
    """
    _authorize_sms_target(person_id, current_user, db)

    # Get SMS preferences
    sms_pref = db.query(SmsPreference).filter(SmsPreference.person_id == person_id).first()

    if not sms_pref:
        raise HTTPException(
            status_code=404, detail="SMS preferences not found. Verify phone first."
        )

    if not sms_pref.verified:
        raise HTTPException(
            status_code=403, detail="Phone must be verified before updating preferences"
        )

    # Validate notification types
    valid_types = ["assignment", "reminder", "change", "cancellation"]
    for notification_type in request.notification_types:
        if notification_type not in valid_types:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid notification type: {notification_type}. Valid: {', '.join(valid_types)}",
            )

    # Validate language
    valid_languages = ["en", "es", "pt", "zh-CN", "zh-TW", "fr"]
    if request.language not in valid_languages:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid language: {request.language}. Valid: {', '.join(valid_languages)}",
        )

    # Update preferences
    sms_pref.notification_types = request.notification_types
    sms_pref.language = request.language
    db.commit()

    return {
        "message": "SMS preferences updated successfully",
        "notification_types": sms_pref.notification_types,
        "language": sms_pref.language,
    }


@router.get("/organizations/{org_id}/sms-usage", response_model=SmsUsageStatsResponse)
def get_sms_usage_stats(
    org_id: str,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Get SMS usage statistics for organization (admin only).

    Returns current month usage with budget tracking.
    """

    from api.models import SmsUsage

    if current_admin.org_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied: wrong organization")

    # Get current month usage
    current_month = utcnow().strftime("%Y-%m")

    usage = (
        db.query(SmsUsage)
        .filter(SmsUsage.organization_id == org_id, SmsUsage.month_year == current_month)
        .first()
    )

    if not usage:
        # No usage this month - return zeros
        return SmsUsageStatsResponse(
            month_year=current_month,
            messages_sent=0,
            messages_delivered=0,
            messages_failed=0,
            total_cost_cents=0,
            budget_limit_cents=10000,  # Default $100 budget
            budget_used_percentage=0.0,
            messages_remaining=None,
        )

    # Calculate budget percentage
    budget_used_percentage = (
        (usage.total_cost_cents / usage.budget_limit_cents * 100)
        if usage.budget_limit_cents > 0
        else 0
    )

    # Calculate messages remaining (if budget set)
    messages_remaining = None
    if usage.budget_limit_cents > 0:
        remaining_cents = usage.budget_limit_cents - usage.total_cost_cents
        # Average cost per message: 0.79 cents (rounded to 1 cent)
        messages_remaining = max(0, int(remaining_cents / 1))

    messages_sent = (
        usage.assignment_count + usage.reminder_count + usage.broadcast_count + usage.system_count
    )
    month_start = utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    delivered_count = (
        db.query(SmsMessage)
        .filter(
            SmsMessage.organization_id == org_id,
            SmsMessage.created_at >= month_start,
            SmsMessage.status == "delivered",
        )
        .count()
    )
    failed_count = (
        db.query(SmsMessage)
        .filter(
            SmsMessage.organization_id == org_id,
            SmsMessage.created_at >= month_start,
            SmsMessage.status.in_(["failed", "undelivered", "canceled"]),
        )
        .count()
    )

    return SmsUsageStatsResponse(
        month_year=usage.month_year,
        messages_sent=messages_sent,
        messages_delivered=delivered_count,
        messages_failed=failed_count,
        total_cost_cents=usage.total_cost_cents,
        budget_limit_cents=usage.budget_limit_cents,
        budget_used_percentage=round(budget_used_percentage, 2),
        messages_remaining=messages_remaining,
    )


# ============================================================================
# Assignment Notification Endpoints
# ============================================================================


@router.post("/send-assignment-notification")
def send_assignment_notification_api(
    request: SendAssignmentNotificationRequest,
    background_tasks: BackgroundTasks,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Send assignment notification SMS to volunteer (admin only).

    Queues background task for async delivery.
    """
    event = (
        db.query(Event)
        .filter(Event.id == request.event_id, Event.org_id == current_admin.org_id)
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {request.event_id} not found")

    person = (
        db.query(Person)
        .filter(Person.id == request.person_id, Person.org_id == current_admin.org_id)
        .first()
    )
    if not person:
        raise HTTPException(status_code=404, detail="Assignment target not found")

    assignment = (
        db.query(Assignment)
        .filter(
            Assignment.id == request.assignment_id,
            Assignment.event_id == request.event_id,
            Assignment.person_id == request.person_id,
        )
        .first()
    )
    if not assignment:
        raise HTTPException(status_code=404, detail=f"Assignment {request.assignment_id} not found")

    # Queue Celery task
    task = send_assignment_notification.delay(
        assignment_id=request.assignment_id,
        event_id=request.event_id,
        person_id=request.person_id,
        organization_id=event.org_id,
        language=request.language,
    )

    return {
        "status": "queued",
        "message": "Assignment notification queued for delivery",
        "task_id": task.id,
        "assignment_id": request.assignment_id,
        "event_id": request.event_id,
        "person_id": request.person_id,
    }


@router.post("/send-event-reminder")
def send_event_reminder_api(
    request: SendEventReminderRequest,
    background_tasks: BackgroundTasks,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Send reminder SMS to all assigned volunteers for event (admin only).

    Queues background task for async delivery.
    """
    event = (
        db.query(Event)
        .filter(Event.id == request.event_id, Event.org_id == current_admin.org_id)
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {request.event_id} not found")

    # Queue Celery task
    task = send_event_reminder.delay(
        event_id=request.event_id,
        organization_id=event.org_id,
        hours_before=request.hours_before,
        language=request.language,
    )

    return {
        "status": "queued",
        "message": f"Reminder queued for {request.hours_before}h before event",
        "task_id": task.id,
        "event_id": request.event_id,
    }


@router.post("/send-broadcast", response_model=BroadcastResponse)
def send_broadcast_api(
    request: SendBroadcastRequest,
    current_admin: Person = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Send broadcast SMS to multiple volunteers (admin only).

    Max 200 recipients per broadcast.
    Respects rate limits, quiet hours, and opt-outs.
    """
    if not request.recipient_ids:
        raise HTTPException(status_code=422, detail="recipient_ids cannot be empty")

    if len(request.recipient_ids) > 200:
        raise HTTPException(status_code=422, detail="Maximum 200 recipients per broadcast")

    if len(set(request.recipient_ids)) != len(request.recipient_ids):
        raise HTTPException(status_code=422, detail="recipient_ids must be unique")

    organization_id = current_admin.org_id
    recipients = (
        db.query(Person.id)
        .filter(Person.id.in_(request.recipient_ids), Person.org_id == organization_id)
        .all()
    )
    if {person_id for (person_id,) in recipients} != set(request.recipient_ids):
        raise HTTPException(status_code=404, detail="One or more SMS recipients were not found")

    # Queue Celery task
    task = send_broadcast_message.delay(
        recipient_ids=request.recipient_ids,
        message_text=request.message_text,
        organization_id=organization_id,
        is_urgent=request.is_urgent,
    )

    return BroadcastResponse(
        status="queued",
        total_recipients=len(request.recipient_ids),
        queued_count=0,  # Will be updated when task completes
        skipped_count=0,
        estimated_cost_cents=0,  # Will be calculated during send
        message=f"Broadcast queued for {len(request.recipient_ids)} recipients (task_id: {task.id})",
    )


# ============================================================================
# Twilio Webhook Endpoints
# ============================================================================


@router.post("/webhook/incoming-sms")
async def twilio_incoming_sms_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle incoming SMS from Twilio webhook.

    Processes YES/NO/STOP/START/HELP replies from volunteers.
    """
    try:
        form_data = await _validated_twilio_form(request, "TWILIO_INCOMING_SMS_URL")
        from_phone = form_data.get("From")
        message_text = form_data.get("Body")
        twilio_message_sid = form_data.get("MessageSid")

        if not from_phone or not message_text or not twilio_message_sid:
            raise HTTPException(status_code=422, detail="Missing required fields")

        sms_service = SMSService()
        result = sms_service.process_incoming_reply(
            db=db,
            from_phone=from_phone,
            message_text=message_text,
            twilio_message_sid=twilio_message_sid,
        )

        return {
            "status": "duplicate" if result.get("duplicate") else "processed",
            "reply_type": result["reply_type"],
            "action_taken": result["action_taken"],
        }

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=422, detail="Unable to process SMS callback")


@router.post("/webhook/delivery-status")
async def twilio_delivery_status_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle SMS delivery status updates from Twilio webhook.

    Updates message status (delivered, failed, undelivered).
    """
    form_data = await _validated_twilio_form(request, "TWILIO_STATUS_CALLBACK_URL")
    message_sid = form_data.get("MessageSid")
    message_status = form_data.get("MessageStatus")
    if not message_sid or not message_status:
        raise HTTPException(status_code=422, detail="Missing required fields")

    allowed_statuses = set(_DELIVERY_PROGRESS) | _DELIVERY_FAILURES
    if message_status not in allowed_statuses:
        raise HTTPException(status_code=422, detail="Invalid delivery status")

    sms_message = db.query(SmsMessage).filter(SmsMessage.twilio_message_sid == message_sid).first()
    if not sms_message:
        raise HTTPException(status_code=404, detail="SMS message not found")
    current_status = str(sms_message.status)
    is_duplicate = (
        current_status == message_status
        or current_status in _DELIVERY_FAILURES
        or current_status == "read"
        or (current_status == "delivered" and message_status != "read")
    )
    if current_status in _DELIVERY_PROGRESS and message_status in _DELIVERY_PROGRESS:
        is_duplicate = is_duplicate or (
            _DELIVERY_PROGRESS[message_status] <= _DELIVERY_PROGRESS[current_status]
        )
    if is_duplicate:
        return {
            "status": "duplicate",
            "message_sid": message_sid,
            "updated_status": sms_message.status,
        }

    sms_message.status = message_status
    if message_status in {"delivered", "read"} and not sms_message.delivered_at:
        sms_message.delivered_at = utcnow()
    elif message_status in _DELIVERY_FAILURES:
        sms_message.failed_at = utcnow()
        sms_message.error_message = form_data.get("ErrorMessage", "Unknown error")
    db.commit()

    return {"status": "ok", "message_sid": message_sid, "updated_status": message_status}
