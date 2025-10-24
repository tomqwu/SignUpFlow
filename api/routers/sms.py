"""
SMS API endpoints for notifications and preferences management.

Provides endpoints for:
- Sending assignment notifications
- Phone verification
- SMS preference management
- Broadcast messages
- Incoming webhook handling
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from api.database import get_db
from api.dependencies import get_current_user, verify_admin_access
from api.models import Person, Event, Assignment, SmsPreference
from api.services.sms_service import SMSService
from api.tasks.sms_tasks import (
    send_assignment_notification,
    send_event_reminder,
    send_schedule_change_notification,
    send_broadcast_message,
)

router = APIRouter(prefix="/api/sms", tags=["sms"])


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
    country_code: Optional[str] = None
    error: Optional[str] = None


class VerificationCodeRequest(BaseModel):
    """Request to generate and send verification code."""

    person_id: int
    phone_number: str = Field(..., description="Phone number in E.164 format")


class VerificationCodeResponse(BaseModel):
    """Response from verification code generation."""

    message: str
    expires_at: str
    phone_number: str


class VerifyCodeRequest(BaseModel):
    """Request to verify SMS code."""

    person_id: int
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

    recipient_ids: List[int] = Field(..., description="List of person IDs (max 200)")
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
        raise HTTPException(
            status_code=500, detail=f"Phone verification failed: {str(e)}"
        )


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
    # Verify user can only request code for themselves (unless admin)
    if current_user.id != str(request.person_id) and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Can only verify your own phone")

    sms_service = SMSService()

    try:
        code = sms_service.generate_verification_code(
            db=db, person_id=request.person_id, phone_number=request.phone_number
        )

        from datetime import datetime, timedelta

        expires_at = (datetime.utcnow() + timedelta(minutes=10)).isoformat()

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
    # Verify user can only verify their own code (unless admin)
    if current_user.id != str(request.person_id) and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Can only verify your own phone")

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

    notification_types: List[str] = Field(
        ..., description="List of notification types: assignment, reminder, change, cancellation"
    )
    language: str = Field(default="en", description="Preferred language for SMS: en, es, pt, zh-CN, zh-TW, fr")


class SmsUsageStatsResponse(BaseModel):
    """Response with SMS usage statistics for organization."""

    month_year: str
    messages_sent: int
    messages_delivered: int
    messages_failed: int
    total_cost_cents: int
    budget_limit_cents: int
    budget_used_percentage: float
    messages_remaining: Optional[int] = None


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
    # Authorization: user can update own preferences OR admin can update any
    person_id_int = int(person_id.split("_")[-1])
    current_user_id_int = int(current_user.id.split("_")[-1])

    is_admin = "admin" in (current_user.roles if isinstance(current_user.roles, list) else [])

    if person_id_int != current_user_id_int and not is_admin:
        raise HTTPException(status_code=403, detail="Can only update your own preferences")

    # Get SMS preferences
    sms_pref = db.query(SmsPreference).filter(SmsPreference.person_id == person_id_int).first()

    if not sms_pref:
        raise HTTPException(status_code=404, detail="SMS preferences not found. Verify phone first.")

    if not sms_pref.verified:
        raise HTTPException(status_code=403, detail="Phone must be verified before updating preferences")

    # Validate notification types
    valid_types = ["assignment", "reminder", "change", "cancellation"]
    for notification_type in request.notification_types:
        if notification_type not in valid_types:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid notification type: {notification_type}. Valid: {', '.join(valid_types)}"
            )

    # Validate language
    valid_languages = ["en", "es", "pt", "zh-CN", "zh-TW", "fr"]
    if request.language not in valid_languages:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid language: {request.language}. Valid: {', '.join(valid_languages)}"
        )

    # Update preferences
    sms_pref.notification_types = request.notification_types
    sms_pref.language = request.language
    db.commit()

    return {
        "message": "SMS preferences updated successfully",
        "notification_types": sms_pref.notification_types,
        "language": sms_pref.language
    }


@router.get("/organizations/{org_id}/sms-usage", response_model=SmsUsageStatsResponse)
def get_sms_usage_stats(
    org_id: int,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db),
):
    """
    Get SMS usage statistics for organization (admin only).

    Returns current month usage with budget tracking.
    """
    from api.models import SmsUsage
    from datetime import datetime

    # Verify admin belongs to organization
    admin_org_id = int(admin.org_id.split("_")[-1])
    if admin_org_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied: wrong organization")

    # Get current month usage
    current_month = datetime.utcnow().strftime("%Y-%m")

    usage = (
        db.query(SmsUsage)
        .filter(
            SmsUsage.organization_id == org_id,
            SmsUsage.month_year == current_month
        )
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
            budget_limit_cents=100000,  # Default $1000 budget
            budget_used_percentage=0.0,
            messages_remaining=None
        )

    # Calculate budget percentage
    budget_used_percentage = (usage.total_cost_cents / usage.budget_limit_cents * 100) if usage.budget_limit_cents > 0 else 0

    # Calculate messages remaining (if budget set)
    messages_remaining = None
    if usage.budget_limit_cents > 0:
        remaining_cents = usage.budget_limit_cents - usage.total_cost_cents
        # Average cost per message: 0.79 cents (rounded to 1 cent)
        messages_remaining = max(0, int(remaining_cents / 1))

    return SmsUsageStatsResponse(
        month_year=usage.month_year,
        messages_sent=usage.messages_sent,
        messages_delivered=usage.messages_delivered,
        messages_failed=usage.messages_failed,
        total_cost_cents=usage.total_cost_cents,
        budget_limit_cents=usage.budget_limit_cents,
        budget_used_percentage=round(budget_used_percentage, 2),
        messages_remaining=messages_remaining
    )


# ============================================================================
# Assignment Notification Endpoints
# ============================================================================


@router.post("/send-assignment-notification")
def send_assignment_notification_api(
    request: SendAssignmentNotificationRequest,
    background_tasks: BackgroundTasks,
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db),
):
    """
    Send assignment notification SMS to volunteer (admin only).

    Queues background task for async delivery.
    """
    # Verify event exists
    event = db.query(Event).filter(Event.id == request.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {request.event_id} not found")

    # Verify assignment exists
    assignment = db.query(Assignment).filter(Assignment.id == request.assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=404, detail=f"Assignment {request.assignment_id} not found"
        )

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
    admin: Person = Depends(verify_admin_access),
    db: Session = Depends(get_db),
):
    """
    Send reminder SMS to all assigned volunteers for event (admin only).

    Queues background task for async delivery.
    """
    # Verify event exists
    event = db.query(Event).filter(Event.id == request.event_id).first()
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
    admin: Person = Depends(verify_admin_access),
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
        raise HTTPException(
            status_code=422, detail="Maximum 200 recipients per broadcast"
        )

    # Get organization ID from admin
    organization_id = admin.org_id

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
    sms_service = SMSService()

    try:
        # Parse Twilio request
        form_data = await request.form()
        from_phone = form_data.get("From")
        message_text = form_data.get("Body")
        twilio_message_sid = form_data.get("MessageSid")

        if not from_phone or not message_text:
            raise HTTPException(status_code=422, detail="Missing required fields")

        # Process reply
        result = sms_service.process_incoming_reply(
            db=db,
            from_phone=from_phone,
            message_text=message_text,
            twilio_message_sid=twilio_message_sid,
        )

        # Return TwiML response
        return {
            "status": "processed",
            "reply_type": result["reply_type"],
            "action_taken": result["action_taken"],
        }

    except ValueError as e:
        # Unknown phone number or invalid request
        return {"status": "error", "message": str(e)}
    except Exception as e:
        # Log error but don't expose to Twilio
        print(f"Error processing incoming SMS: {str(e)}")
        return {"status": "error", "message": "Failed to process message"}


@router.post("/webhook/delivery-status")
async def twilio_delivery_status_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle SMS delivery status updates from Twilio webhook.

    Updates message status (delivered, failed, undelivered).
    """
    try:
        # Parse Twilio request
        form_data = await request.form()
        message_sid = form_data.get("MessageSid")
        message_status = form_data.get("MessageStatus")

        if not message_sid or not message_status:
            raise HTTPException(status_code=422, detail="Missing required fields")

        # Update message status in database
        from api.models import SmsMessage
        from datetime import datetime

        sms_message = (
            db.query(SmsMessage)
            .filter(SmsMessage.twilio_message_sid == message_sid)
            .first()
        )

        if sms_message:
            sms_message.status = message_status

            if message_status == "delivered":
                sms_message.delivered_at = datetime.utcnow()
            elif message_status in ["failed", "undelivered"]:
                sms_message.failed_at = datetime.utcnow()
                sms_message.error_message = form_data.get("ErrorMessage", "Unknown error")

            db.commit()

        return {"status": "ok", "message_sid": message_sid, "updated_status": message_status}

    except Exception as e:
        print(f"Error processing delivery status: {str(e)}")
        return {"status": "error", "message": "Failed to update status"}
