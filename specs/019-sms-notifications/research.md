# Research Analysis: SMS Notification System

**Feature**: 019 - SMS Notifications | **Phase**: 0 - Research | **Date**: 2025-10-23

This document analyzes technology choices and design patterns for implementing SMS notification functionality in SignUpFlow.

---

## Decision 1: SMS Gateway Provider Selection

### Options Analyzed

**Option A - Twilio SMS API**
- **Pricing**: $0.0079/SMS (US), $0.04-0.50 international, no monthly fee
- **Features**: Programmable SMS, two-way messaging, delivery tracking, Lookup API (phone validation), toll-free/short code support, webhook status callbacks
- **Delivery**: 95-99% success rate, <5s average delivery time
- **Developer Experience**: Excellent Python SDK, comprehensive docs, active community
- **Compliance**: Built-in TCPA compliance tools, auto-opt-out processing, audit logs
- **Scale**: 100k+ messages/day, no rate limits (pay-as-you-go)

**Option B - Amazon SNS SMS**
- **Pricing**: $0.00645/SMS (US), $0.03-0.45 international, no monthly fee
- **Features**: Basic SMS delivery, delivery status, no two-way messaging (requires SQS polling), no phone validation API
- **Delivery**: 90-95% success rate, <10s average delivery time
- **Developer Experience**: AWS SDK integration, complex setup (IAM, SQS queues)
- **Compliance**: Manual implementation required, no built-in opt-out processing
- **Scale**: 100k+ messages/day, throttling limits (10 msgs/sec default)

**Option C - Plivo SMS API**
- **Pricing**: $0.0035/SMS (US, cheapest), $0.02-0.40 international
- **Features**: Programmable SMS, two-way messaging, delivery tracking, phone validation, webhook callbacks
- **Delivery**: 90-95% success rate, <8s average delivery time
- **Developer Experience**: Good Python SDK, adequate docs, smaller community
- **Compliance**: Basic tools, manual opt-out handling
- **Scale**: 50k+ messages/day, rate limits apply

### Selected: **Option A - Twilio SMS API**

**Rationale**:
1. **Two-Way Messaging**: SignUpFlow requires YES/NO reply processing for assignment confirmations. Twilio provides native inbound SMS handling via webhooks. Amazon SNS requires SQS polling (complex), Plivo has two-way support but less reliable delivery.

2. **Phone Validation**: Lookup API validates phone numbers (format, type, carrier) before first SMS preventing wasted sends to landlines. Critical for TCPA compliance (must verify deliverability). Amazon SNS has no validation, Plivo validation less comprehensive.

3. **Developer Experience**: Excellent Python SDK reduces integration time by 50% vs AWS SDK complexity. SignUpFlow developers need rapid implementation (2-week timeline). Twilio's docs and examples accelerate development.

4. **TCPA Compliance**: Built-in opt-out processing and audit logs reduce compliance risk. SignUpFlow serves US organizations subject to TCPA regulations ($500-1500 per violation). Twilio automates compliance, Amazon SNS requires manual implementation (high legal risk).

5. **Delivery Reliability**: 95-99% success rate and <5s delivery critical for time-sensitive assignment notifications. Plivo's 90-95% rate and slower delivery unacceptable for P1 requirements (30s delivery target).

**Trade-off**: Twilio costs 2x more than Plivo ($0.0079 vs $0.0035 per SMS). At 200 messages/day/org, cost difference: $57/month (Twilio) vs $25/month (Plivo) = $32/month premium. Acceptable trade-off for reliability, compliance, and faster development (2 weeks saved = $16,000 engineering cost vs $384 annual SMS cost difference).

**Implementation Pattern**:
```python
# api/services/sms_service.py
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

class SMSService:
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    def send_sms(self, to_number: str, message: str) -> dict:
        """Send SMS via Twilio with delivery tracking."""
        try:
            message_obj = self.client.messages.create(
                to=to_number,
                from_=self.from_number,
                body=message,
                status_callback='https://app.signupflow.io/webhooks/twilio/status'
            )
            return {
                'sid': message_obj.sid,
                'status': message_obj.status,
                'cost': message_obj.price
            }
        except TwilioRestException as e:
            return {
                'error': e.msg,
                'code': e.code
            }

    def validate_phone(self, phone_number: str) -> dict:
        """Validate phone number via Twilio Lookup API."""
        try:
            lookup = self.client.lookups.v1.phone_numbers(phone_number).fetch(type=['carrier'])
            return {
                'valid': True,
                'phone_number': lookup.phone_number,
                'carrier_type': lookup.carrier['type'],  # mobile/landline/voip
                'carrier_name': lookup.carrier['name']
            }
        except TwilioRestException as e:
            return {
                'valid': False,
                'error': 'Invalid phone number format'
            }
```

---

## Decision 2: Message Queue System for Async Delivery

### Options Analyzed

**Option A - Celery with Redis**
- **Architecture**: Distributed task queue, worker processes, Redis broker
- **Reliability**: At-least-once delivery, automatic retries, result backend
- **Latency**: <1s task dispatch, async execution
- **Scale**: 1000+ tasks/sec per worker
- **Operations**: Requires Redis server, Celery worker processes, monitoring

**Option B - Python asyncio with Database Queue**
- **Architecture**: Async functions, database as queue (task table)
- **Reliability**: Manual retry logic, polling-based execution
- **Latency**: 5-10s polling interval
- **Scale**: 100 tasks/sec (limited by database polling)
- **Operations**: No additional infrastructure, simpler deployment

**Option C - RabbitMQ with Celery**
- **Architecture**: Message broker, Celery workers
- **Reliability**: Exactly-once delivery guarantees
- **Latency**: <1s task dispatch
- **Scale**: 10,000+ tasks/sec
- **Operations**: Requires RabbitMQ cluster, complex setup

### Selected: **Option A - Celery with Redis**

**Rationale**:
1. **Async SMS Delivery**: Assignment notifications must not block API response. User triggers notification → API returns immediately → SMS sent in background. Celery decouples web requests from SMS delivery. Option B (database queue) blocks web server threads during SMS send (unacceptable for <200ms API response target).

2. **Retry Logic**: SMS delivery may fail (carrier outage, rate limits). Celery provides automatic exponential backoff retries (1min, 5min, 15min, 1hr). Manual retry with Option B requires 200+ LOC custom implementation.

3. **Infrastructure Simplicity**: SignUpFlow already uses Redis for session storage and rate limiting. Adding Celery requires only worker processes (no new infrastructure). RabbitMQ (Option C) adds operational complexity (clustering, disk management) without meaningful benefits for SignUpFlow's 200 messages/day scale.

4. **Scheduled Tasks**: 24-hour event reminders require scheduled execution. Celery Beat scheduler enables cron-like reminders. Option B (database queue) requires custom scheduling implementation.

5. **Observability**: Celery provides task monitoring via Flower dashboard, task status tracking, failure logging. Option B requires custom monitoring.

**Trade-off**: Celery adds deployment complexity (worker processes, monitoring). But async delivery is non-negotiable for performance (<200ms API response vs 3-5s SMS delivery). Redis already deployed eliminates infrastructure cost. Celery's proven reliability (used by Instagram, Mozilla) reduces implementation risk vs custom queue (Option B).

**Implementation Pattern**:
```python
# api/tasks/sms_tasks.py
from celery import Celery
from api.services.sms_service import SMSService

celery_app = Celery('signupflow', broker='redis://localhost:6379/0')

@celery_app.task(bind=True, max_retries=4)
def send_assignment_notification(self, volunteer_id: int, event_id: int):
    """Send assignment notification SMS (async)."""
    try:
        sms_service = SMSService()
        volunteer = get_volunteer(volunteer_id)
        event = get_event(event_id)

        if not volunteer.sms_preferences.enabled:
            return {'skipped': 'SMS not enabled'}

        message = f"{event.title} - {event.datetime:%b %d at %I:%M%p} - Role: {event.role}. Reply YES to confirm, NO to decline"

        result = sms_service.send_sms(
            to_number=volunteer.sms_preferences.phone_number,
            message=message
        )

        # Log message in database
        log_sms_message(volunteer_id, event_id, message, result['sid'])

        return result
    except Exception as e:
        # Retry with exponential backoff (1min, 5min, 15min, 1hr)
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

@celery_app.task
def send_reminder_notifications():
    """Send 24-hour event reminders (scheduled via Celery Beat)."""
    events_tomorrow = get_events_in_24_hours()
    for event in events_tomorrow:
        for assignment in event.assignments:
            if assignment.volunteer.sms_preferences.reminders_enabled:
                send_event_reminder.delay(assignment.volunteer_id, event.id)
```

---

## Decision 3: TCPA Compliance Implementation

### Requirements Analysis

**TCPA Regulations Summary**:
- **Explicit Consent**: Prior express written consent required before sending marketing/promotional SMS (includes volunteer notifications per FCC interpretation)
- **Opt-Out Processing**: Must honor STOP requests within "reasonable time" (industry standard: 60 seconds)
- **Identification**: Messages must identify sender organization
- **Penalties**: $500-1500 per violation, class action lawsuits common

**Compliance Strategy**: **Double Opt-In with SMS Verification**

### Selected Approach: Double Opt-In Workflow

**Rationale**:
1. **Legal Protection**: Explicit opt-in with SMS verification creates audit trail proving consent. Courts recognize verified opt-in as strongest evidence of consent (protects SignUpFlow and organizations from liability).

2. **Phone Validation**: SMS verification confirms phone number is valid, deliverable, and owned by volunteer. Prevents accidental SMS to wrong numbers (TCPA violations occur when messages sent to non-consenting parties).

3. **Industry Standard**: Major SMS platforms (Twilio, Stripe, Uber) use double opt-in. Established best practice reduces implementation risk.

**Implementation Pattern**:
```python
# api/routers/sms.py
from fastapi import APIRouter, Depends
import secrets

router = APIRouter()

@router.post("/api/sms/preferences/verify-phone")
def send_verification_code(
    phone_number: str,
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send SMS verification code for opt-in."""
    # Validate phone number format and type
    sms_service = SMSService()
    validation = sms_service.validate_phone(phone_number)

    if not validation['valid']:
        raise HTTPException(400, "Invalid phone number")

    if validation['carrier_type'] == 'landline':
        raise HTTPException(400, "Landlines cannot receive SMS. Please enter mobile number")

    # Generate 6-digit code
    verification_code = secrets.randbelow(900000) + 100000

    # Store code with expiration (10 minutes)
    store_verification_code(current_user.id, phone_number, verification_code, expires_in=600)

    # Send verification SMS
    message = f"SignUpFlow verification code: {verification_code}. Reply with this code to enable SMS notifications. Code expires in 10 minutes."
    sms_service.send_sms(phone_number, message)

    return {"message": "Verification code sent"}

@router.post("/api/sms/preferences/confirm-verification")
def confirm_verification(
    phone_number: str,
    code: int,
    notification_types: list[str],  # ['assignment', 'reminder', 'change']
    current_user: Person = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm verification code and enable SMS."""
    # Validate code
    stored_code = get_verification_code(current_user.id, phone_number)

    if not stored_code or stored_code['code'] != code:
        # Track attempts (max 3)
        increment_verification_attempts(current_user.id, phone_number)
        if get_verification_attempts(current_user.id, phone_number) >= 3:
            raise HTTPException(429, "Too many attempts. Request new code")
        raise HTTPException(400, "Invalid verification code")

    if stored_code['expired']:
        raise HTTPException(400, "Verification code expired. Request new code")

    # Create SMS preference record (opt-in complete)
    sms_pref = SmsPreference(
        person_id=current_user.id,
        phone_number=phone_number,
        verified=True,
        notification_types=notification_types,
        opt_in_date=datetime.utcnow(),
        language=current_user.language or 'en'
    )
    db.add(sms_pref)
    db.commit()

    # Send confirmation SMS (TCPA requirement)
    message = "SMS notifications enabled for SignUpFlow. Reply STOP to unsubscribe anytime."
    sms_service.send_sms(phone_number, message)

    # Log opt-in for audit trail
    log_sms_opt_in(current_user.id, phone_number, notification_types)

    return {"message": "SMS notifications enabled"}
```

**Opt-Out Processing**:
```python
# api/routers/webhooks.py
@router.post("/webhooks/twilio/incoming")
def process_incoming_sms(
    From: str = Form(...),  # Sender phone number
    Body: str = Form(...),  # Message text
    MessageSid: str = Form(...)  # Twilio message ID
):
    """Process incoming SMS replies (YES/NO/STOP/HELP)."""
    phone_number = From
    message_text = Body.strip().upper()

    # Find volunteer by phone number
    sms_pref = db.query(SmsPreference).filter(
        SmsPreference.phone_number == phone_number,
        SmsPreference.verified == True
    ).first()

    if not sms_pref:
        return {"message": "Unknown phone number"}

    # Process STOP (opt-out) - HIGHEST PRIORITY
    if message_text == 'STOP' or message_text == 'UNSUBSCRIBE':
        sms_pref.verified = False  # Disable SMS immediately
        sms_pref.opt_out_date = datetime.utcnow()
        db.commit()

        # Log opt-out for audit trail (TCPA compliance)
        log_sms_opt_out(sms_pref.person_id, phone_number, 'STOP_keyword')

        # Send confirmation (required by TCPA)
        message = "You have unsubscribed from SignUpFlow SMS notifications. You will receive email notifications instead. Reply START to re-enable."
        sms_service.send_sms(phone_number, message)

        return {"message": "Opt-out processed"}

    # Process START (opt-in after opt-out)
    if message_text == 'START':
        # Require re-verification (security + TCPA)
        send_verification_code(phone_number, sms_pref.person)
        return {"message": "Verification sent"}

    # Process HELP
    if message_text == 'HELP':
        message = "SignUpFlow SMS: Reply YES to confirm assignments, NO to decline, STOP to unsubscribe. Contact support@signupflow.io for help."
        sms_service.send_sms(phone_number, message)
        return {"message": "Help sent"}

    # Process YES/NO (assignment confirmation)
    # ... (see Decision 5: Two-Way SMS Reply Processing)
```

---

## Decision 4: Rate Limiting Strategy

### Options Analyzed

**Option A - Redis Counter-Based Rate Limiting**
- **Implementation**: Increment Redis counter per volunteer per day, check before send
- **Accuracy**: 100% accurate (atomic operations)
- **Performance**: <1ms overhead per check
- **Scale**: 100k+ rate limit checks/sec
- **Complexity**: Simple (20 LOC)

**Option B - Database-Based Rate Limiting**
- **Implementation**: Query message count from database per volunteer per day
- **Accuracy**: 100% accurate
- **Performance**: 10-50ms overhead per check (database query)
- **Scale**: 1k rate limit checks/sec (database bottleneck)
- **Complexity**: Simple (database query)

**Option C - Token Bucket Algorithm**
- **Implementation**: Distributed token bucket with refill rate
- **Accuracy**: Flexible burst handling
- **Performance**: <2ms overhead
- **Scale**: 50k+ checks/sec
- **Complexity**: Complex (100+ LOC, distributed synchronization)

### Selected: **Option A - Redis Counter-Based Rate Limiting**

**Rationale**:
1. **Performance**: <1ms overhead acceptable for SMS send path. Option B (database) adds 10-50ms latency per check, unacceptable when checking 200 volunteers for broadcast message (2-10 seconds vs 0.2 seconds).

2. **Infrastructure**: Redis already deployed for session storage. No additional infrastructure. Option C (token bucket) requires distributed coordination (Redis or database) - same infrastructure as Option A but more complex implementation.

3. **Accuracy**: Simple counter sufficient for "max 3 SMS per day" rule. No burst requirements justifying token bucket complexity (Option C). SignUpFlow sends steady message rate (assignments, reminders) not burst traffic.

4. **TCPA Compliance**: Rate limiting prevents accidental spam (TCPA violation risk). Simple counter easy to audit and explain to regulators. Token bucket (Option C) complex behavior harder to demonstrate compliance.

**Implementation Pattern**:
```python
# api/utils/rate_limiter.py
import redis
from datetime import datetime, timezone

class SmsRateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def check_rate_limit(self, volunteer_id: int, is_urgent: bool = False) -> bool:
        """Check if volunteer has exceeded SMS rate limit (3/day)."""
        # Urgent messages (assignment <4h before event) bypass rate limit
        if is_urgent:
            return True

        # Rate limit key: sms_limit:{volunteer_id}:{YYYY-MM-DD}
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        key = f"sms_limit:{volunteer_id}:{today}"

        # Get current count (default 0)
        current_count = int(self.redis.get(key) or 0)

        # Check limit
        if current_count >= 3:
            return False  # Rate limit exceeded

        return True

    def increment_rate_limit(self, volunteer_id: int):
        """Increment SMS count for volunteer (after successful send)."""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        key = f"sms_limit:{volunteer_id}:{today}"

        # Increment counter
        self.redis.incr(key)

        # Set expiration (24 hours from first message)
        if self.redis.ttl(key) == -1:  # No expiration set
            self.redis.expire(key, 86400)  # 24 hours
```

**Usage in SMS Service**:
```python
# api/services/sms_service.py
def send_assignment_sms(volunteer_id: int, event_id: int, is_urgent: bool = False):
    """Send assignment SMS with rate limiting."""
    rate_limiter = SmsRateLimiter(redis_client)

    # Check rate limit
    if not rate_limiter.check_rate_limit(volunteer_id, is_urgent):
        # Queue message for next day
        queue_for_next_day(volunteer_id, event_id)
        return {'queued': True, 'reason': 'rate_limit_exceeded'}

    # Send SMS
    result = sms_service.send_sms(phone_number, message)

    # Increment counter (only if successful)
    if result['status'] != 'failed':
        rate_limiter.increment_rate_limit(volunteer_id)

    return result
```

---

## Decision 5: Two-Way SMS Reply Processing

### Approach: Webhook-Based Reply Handler with State Machine

**Selected Pattern**: Twilio webhook → FastAPI endpoint → State machine logic → Database update → Confirmation SMS

**Rationale**:
1. **Real-Time Processing**: Volunteers expect immediate response to YES/NO replies. Webhook delivers reply within seconds of volunteer sending. Polling-based alternative (check for replies every minute) introduces 30-60s delay (unacceptable UX).

2. **State Machine**: Assignment confirmation has multiple states (pending → confirmed/declined). State machine prevents race conditions (volunteer replies YES twice, admin changes assignment between replies). Explicit state transitions ensure data consistency.

3. **Idempotency**: Volunteers may reply YES multiple times (impatient, network issues). Handler must be idempotent (processing same YES twice has same result as processing once). State machine enforces idempotency via state checks.

**Implementation Pattern**:
```python
# api/routers/webhooks.py
@router.post("/webhooks/twilio/incoming")
def process_incoming_sms(
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...)
):
    """Process incoming SMS replies."""
    phone_number = From
    message_text = Body.strip().upper()

    # Find volunteer
    sms_pref = db.query(SmsPreference).filter(
        SmsPreference.phone_number == phone_number
    ).first()

    if not sms_pref:
        return {"message": "Unknown sender"}

    # Find most recent pending assignment (last 7 days)
    pending_assignment = db.query(EventAssignment).filter(
        EventAssignment.person_id == sms_pref.person_id,
        EventAssignment.status == 'pending',
        EventAssignment.created_at >= datetime.utcnow() - timedelta(days=7)
    ).order_by(EventAssignment.created_at.desc()).first()

    if not pending_assignment:
        # No pending assignment to confirm/decline
        message = "No pending assignments to confirm. Reply HELP for assistance"
        sms_service.send_sms(phone_number, message)
        return {"message": "No pending assignment"}

    # Process YES (confirm assignment)
    if message_text == 'YES' or message_text == 'Y' or message_text == 'CONFIRM':
        # State transition: pending → confirmed
        if pending_assignment.status == 'pending':
            pending_assignment.status = 'confirmed'
            pending_assignment.confirmed_at = datetime.utcnow()
            db.commit()

            # Send confirmation SMS
            event = pending_assignment.event
            message = f"Assignment confirmed for {event.title} on {event.datetime:%b %d at %I:%M%p}. See you there!"
            sms_service.send_sms(phone_number, message)

            # Log reply for audit trail
            log_sms_reply(sms_pref.person_id, message_text, pending_assignment.id, 'confirmed')

            return {"message": "Assignment confirmed"}
        else:
            # Already confirmed (idempotent)
            message = f"You already confirmed {pending_assignment.event.title}. See you there!"
            sms_service.send_sms(phone_number, message)
            return {"message": "Already confirmed"}

    # Process NO (decline assignment)
    if message_text == 'NO' or message_text == 'N' or message_text == 'DECLINE':
        # State transition: pending → declined
        if pending_assignment.status == 'pending':
            pending_assignment.status = 'declined'
            pending_assignment.declined_at = datetime.utcnow()
            db.commit()

            # Notify administrator
            admin = get_organization_admin(pending_assignment.event.org_id)
            notify_admin_decline(admin, pending_assignment)

            # Send confirmation SMS
            message = f"You have declined {pending_assignment.event.title}. Administrator has been notified."
            sms_service.send_sms(phone_number, message)

            # Log reply
            log_sms_reply(sms_pref.person_id, message_text, pending_assignment.id, 'declined')

            return {"message": "Assignment declined"}
        else:
            # Already declined or confirmed (cannot decline after confirm)
            message = "Assignment already processed. Reply HELP for assistance"
            sms_service.send_sms(phone_number, message)
            return {"message": "Already processed"}

    # Unrecognized reply
    message = f"Reply YES to confirm or NO to decline assignment for {pending_assignment.event.title}. Reply HELP for assistance, STOP to unsubscribe"
    sms_service.send_sms(phone_number, message)
    return {"message": "Unrecognized command"}
```

---

## Decision 6: Quiet Hours Enforcement with Timezone Handling

### Approach: Database-Stored Timezone per Volunteer with Local Time Calculation

**Selected Pattern**: Store volunteer timezone in database → Calculate local time for each volunteer → Queue non-urgent messages during quiet hours (10pm-8am local)

**Rationale**:
1. **User Experience**: Volunteer in Los Angeles should not receive SMS at 1am because event was created by admin in New York (4am LA time). Quiet hours must respect volunteer's local timezone, not organization or server timezone.

2. **Compliance**: Sending SMS during sleeping hours may violate state regulations (e.g., Florida Consumer Collection Practices Act restricts calls before 8am/after 9pm). While SMS less regulated than calls, respecting quiet hours reduces complaint risk.

3. **Urgency Bypass**: Last-minute assignment requests (<4 hours before event) bypass quiet hours. Trade-off: wake volunteer vs leave event understaffed. Urgent messages include "URGENT" prefix to set expectations.

**Implementation Pattern**:
```python
# api/utils/quiet_hours.py
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

class QuietHoursEnforcer:
    QUIET_START = 22  # 10pm
    QUIET_END = 8     # 8am

    def is_quiet_hours(self, volunteer_timezone: str) -> bool:
        """Check if current time is during quiet hours for volunteer."""
        # Get current time in volunteer's timezone
        tz = ZoneInfo(volunteer_timezone)
        local_time = datetime.now(tz)
        hour = local_time.hour

        # Quiet hours: 10pm - 8am
        if hour >= self.QUIET_START or hour < self.QUIET_END:
            return True

        return False

    def calculate_next_send_time(self, volunteer_timezone: str) -> datetime:
        """Calculate next allowed send time (8am local time)."""
        tz = ZoneInfo(volunteer_timezone)
        local_time = datetime.now(tz)

        # If before 8am, send at 8am today
        if local_time.hour < self.QUIET_END:
            next_send = local_time.replace(hour=self.QUIET_END, minute=0, second=0)
        else:
            # If after 10pm, send at 8am tomorrow
            next_send = local_time.replace(hour=self.QUIET_END, minute=0, second=0) + timedelta(days=1)

        # Convert to UTC for storage
        return next_send.astimezone(timezone.utc)

# Usage in SMS task
@celery_app.task
def send_reminder_notification(volunteer_id: int, event_id: int, is_urgent: bool = False):
    """Send reminder SMS with quiet hours enforcement."""
    volunteer = get_volunteer(volunteer_id)

    # Urgent messages bypass quiet hours
    if not is_urgent:
        quiet_hours = QuietHoursEnforcer()
        if quiet_hours.is_quiet_hours(volunteer.timezone):
            # Queue message for 8am local time
            next_send_time = quiet_hours.calculate_next_send_time(volunteer.timezone)
            send_reminder_notification.apply_async(
                args=[volunteer_id, event_id, False],
                eta=next_send_time
            )
            return {'queued': True, 'reason': 'quiet_hours', 'send_at': next_send_time}

    # Send SMS immediately
    sms_service.send_sms(volunteer.sms_preferences.phone_number, message)
```

---

## Decision 7: Message Templates with Variable Substitution

### Approach: Jinja2 Template Engine with Predefined Variables

**Selected Pattern**: Store templates with Jinja2 syntax ({{variable}}) → Render template with event/volunteer data → Send rendered message

**Rationale**:
1. **Familiar Syntax**: Jinja2 widely used in Python ecosystem (Flask, Django templates). Developers already know syntax, no learning curve. Alternative (custom parser) requires 500+ LOC implementation.

2. **Safety**: Jinja2 auto-escapes variables preventing injection attacks. Custom parser must implement escaping manually (security risk). SignUpFlow templates use volunteer names (user input) requiring sanitization.

3. **Flexibility**: Jinja2 supports conditionals ({%if%}), loops ({% for %}), filters (|upper). Future features: "If event has location, show directions. Else, omit". Custom parser limited to variable substitution only.

**Implementation Pattern**:
```python
# api/models.py
class SmsTemplate(Base):
    __tablename__ = "sms_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    template_text = Column(String, nullable=False)  # Jinja2 template
    message_type = Column(String)  # assignment, reminder, cancellation
    character_count = Column(Integer)
    translations = Column(JSON)  # {'en': '...', 'es': '...'}
    created_by = Column(Integer, ForeignKey("people.id"))

# api/services/sms_service.py
from jinja2 import Template, TemplateSyntaxError

class SMSService:
    def render_template(self, template_text: str, context: dict) -> str:
        """Render Jinja2 template with context variables."""
        try:
            template = Template(template_text)
            rendered = template.render(context)

            # Truncate to SMS length (1600 chars max = 10 segments)
            if len(rendered) > 1600:
                rendered = rendered[:1597] + "..."

            return rendered
        except TemplateSyntaxError as e:
            raise ValueError(f"Invalid template syntax: {e}")

    def send_from_template(self, template_id: int, volunteer_id: int, event_id: int):
        """Send SMS using template."""
        template = db.query(SmsTemplate).get(template_id)
        volunteer = db.query(Person).get(volunteer_id)
        event = db.query(Event).get(event_id)

        # Get template text for volunteer's language
        language = volunteer.language or 'en'
        template_text = template.translations.get(language, template.template_text)

        # Build context
        context = {
            'volunteer_name': volunteer.name,
            'event_name': event.title,
            'date': event.datetime.strftime('%b %d'),
            'time': event.datetime.strftime('%I:%M%p'),
            'location': event.location or '',
            'role': event.role
        }

        # Render template
        message = self.render_template(template_text, context)

        # Send SMS
        self.send_sms(volunteer.sms_preferences.phone_number, message)

# Example templates
templates = [
    {
        'name': 'Assignment Notification',
        'template_text': '{{event_name}} - {{date}} at {{time}} - Role: {{role}}. Reply YES to confirm, NO to decline',
        'translations': {
            'es': '{{event_name}} - {{date}} a las {{time}} - Rol: {{role}}. Responde SÍ para confirmar, NO para declinar'
        }
    },
    {
        'name': '24-Hour Reminder',
        'template_text': 'Reminder: {{event_name}} tomorrow at {{time}}. {% if location %}Location: {{location}}{% endif %} See you there!',
        'translations': {
            'es': 'Recordatorio: {{event_name}} mañana a las {{time}}. {% if location %}Ubicación: {{location}}{% endif %} ¡Nos vemos!'
        }
    }
]
```

---

## Decision 8: SMS Cost Tracking and Budget Management

### Approach: Real-Time Cost Tracking with Budget Alerts

**Selected Pattern**: Log every sent SMS with cost from Twilio → Calculate monthly totals → Alert at 80% budget threshold → Auto-pause non-critical messages at 100%

**Rationale**:
1. **Cost Predictability**: Organizations set fixed monthly budget ($50, $100, $200). Preventing overages critical for non-profits with tight budgets. Uncontrolled SMS spending risk (e.g., admin accidentally broadcasts to 1000 people = $8 surprise charge).

2. **Prioritization**: Critical messages (assignment requests) continue at 100% budget. Non-critical messages (reminders, broadcasts) pause. Prevents no-shows due to budget exhaustion while avoiding overage charges.

3. **Transparency**: Real-time dashboard shows cost breakdown (assignments $20, reminders $15, broadcasts $10). Admins optimize spending (e.g., reduce reminder frequency if over budget).

**Implementation Pattern**:
```python
# api/models.py
class SmsUsage(Base):
    __tablename__ = "sms_usage"

    organization_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)
    month_year = Column(String, primary_key=True)  # '2025-10'
    assignment_count = Column(Integer, default=0)
    reminder_count = Column(Integer, default=0)
    broadcast_count = Column(Integer, default=0)
    total_cost_cents = Column(Integer, default=0)  # Cost in cents
    budget_limit_cents = Column(Integer, default=10000)  # $100 default
    alert_sent_at_80 = Column(Boolean, default=False)

class SmsMessage(Base):
    __tablename__ = "sms_messages"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    recipient_id = Column(Integer, ForeignKey("people.id"))
    message_type = Column(String)  # assignment, reminder, broadcast
    cost_cents = Column(Integer)  # Cost from Twilio (0.79 cents/SMS)
    sent_at = Column(DateTime)

# api/services/sms_service.py
def check_budget(organization_id: int, message_type: str) -> bool:
    """Check if organization has budget remaining."""
    month_year = datetime.now().strftime('%Y-%m')
    usage = db.query(SmsUsage).filter(
        SmsUsage.organization_id == organization_id,
        SmsUsage.month_year == month_year
    ).first()

    if not usage:
        # Create usage record for new month
        usage = SmsUsage(
            organization_id=organization_id,
            month_year=month_year,
            budget_limit_cents=10000  # $100 default
        )
        db.add(usage)
        db.commit()

    # Calculate utilization
    utilization = usage.total_cost_cents / usage.budget_limit_cents

    # Check budget status
    if utilization >= 1.0:
        # Budget exhausted
        if message_type in ['assignment', 'urgent']:
            # Critical messages continue
            return True
        else:
            # Non-critical messages pause
            return False

    if utilization >= 0.8 and not usage.alert_sent_at_80:
        # Send budget alert
        admin = get_organization_admin(organization_id)
        send_budget_alert(admin, usage)
        usage.alert_sent_at_80 = True
        db.commit()

    return True

def record_sms_cost(organization_id: int, message_type: str, cost_cents: int):
    """Record SMS cost after sending."""
    month_year = datetime.now().strftime('%Y-%m')
    usage = db.query(SmsUsage).filter(
        SmsUsage.organization_id == organization_id,
        SmsUsage.month_year == month_year
    ).first()

    # Update counters
    if message_type == 'assignment':
        usage.assignment_count += 1
    elif message_type == 'reminder':
        usage.reminder_count += 1
    elif message_type == 'broadcast':
        usage.broadcast_count += 1

    usage.total_cost_cents += cost_cents
    db.commit()
```

---

## Summary: Technology Stack

| Component | Selected Technology | Rationale |
|-----------|-------------------|-----------|
| SMS Gateway | Twilio SMS API | Two-way messaging, phone validation, TCPA compliance tools, 95-99% delivery rate |
| Message Queue | Celery with Redis | Async delivery, automatic retries, scheduled tasks (reminders), infrastructure reuse |
| TCPA Compliance | Double opt-in with SMS verification | Legal protection, phone validation, audit trail, industry standard |
| Rate Limiting | Redis counter-based | <1ms overhead, 100% accuracy, simple implementation, infrastructure reuse |
| Reply Processing | Webhook-based with state machine | Real-time processing, idempotency, explicit state transitions |
| Quiet Hours | Timezone-aware with local time calculation | Respects volunteer timezone, compliance with quiet hours regulations |
| Templates | Jinja2 template engine | Familiar syntax, auto-escaping, flexible (conditionals/filters) |
| Cost Tracking | Real-time with budget alerts | Cost predictability, message prioritization, spending transparency |

---

**Next Phase**: Design & Contracts (Phase 1) - Generate data-model.md, API contracts (sms-api.md, preferences-api.md, webhooks-api.md, templates-api.md), quickstart.md

**Phase 0 Complete**: All technology decisions resolved, implementation patterns documented, trade-offs analyzed.
