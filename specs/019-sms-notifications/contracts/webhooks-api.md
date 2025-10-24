# API Contract: Twilio Webhook Endpoints

**Feature**: SMS Notification System | **Branch**: `009-sms-notifications` | **Date**: 2025-10-23

Webhook handlers for Twilio delivery status updates and incoming SMS replies (two-way communication).

---

## Overview

Twilio sends HTTP POST requests to SignUpFlow webhook endpoints when:
1. **Message Status Changes**: SMS sent → delivered/failed (delivery tracking)
2. **Incoming SMS Replies**: Volunteer replies YES/NO/STOP/START/HELP (two-way communication)

These webhooks enable real-time status updates without polling and support interactive SMS workflows.

---

## Endpoints

### 1. Message Status Webhook

**Endpoint**: `POST /api/webhooks/twilio/status`

**Purpose**: Receive delivery status updates from Twilio (sent, delivered, failed, undelivered)

**Authentication**: **None** (public webhook, validated via Twilio signature)

**Authorization**: Twilio signature validation (HMAC-SHA256)

**Request Format**: Twilio sends `application/x-www-form-urlencoded`

**Request Parameters** (Form Data):

**Common Fields** (all status updates):
- `MessageSid` (string): Twilio message ID (e.g., "SM1234567890abcdef")
- `MessageStatus` (string): New message status (`sent`, `delivered`, `failed`, `undelivered`)
- `To` (string): Recipient phone number (E.164 format, e.g., "+15551234567")
- `From` (string): Sender phone number (Twilio number)
- `MessagePrice` (string): Message cost (e.g., "-0.0079" for US)
- `MessagePriceCurrency` (string): Currency code (e.g., "USD")

**Additional Fields** (delivery failure):
- `ErrorCode` (string, optional): Twilio error code (e.g., "30003", "30005")
- `ErrorMessage` (string, optional): Human-readable error description

**Twilio Signature Validation**:
```
X-Twilio-Signature: {HMAC-SHA256 signature}
```

### Twilio Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 30003 | Unreachable destination | Phone number invalid or out of service |
| 30004 | Message blocked by carrier | Carrier spam filter or content violation |
| 30005 | Unknown destination | Phone number does not exist |
| 30006 | Landline or unreachable carrier | Phone cannot receive SMS |
| 30007 | Carrier violation or filtering | Message content flagged by carrier |
| 30008 | Unknown error | Twilio internal error, retry recommended |

**Response**:

**Success (200 OK)**: Empty body (Twilio requires 200 OK to mark webhook processed)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response></Response>
```

**Backend Processing** (after responding to Twilio):
1. Validate Twilio signature (HMAC-SHA256)
2. Find message in database by `twilio_message_sid`
3. Update message status in `sms_messages` table
4. Record delivery timestamp (`delivered_at` or `failed_at`)
5. Update cost in `sms_usage` table if `MessagePrice` provided
6. Log error code/message if delivery failed

**Example Twilio Request** (delivered):
```
MessageSid=SM1234567890abcdef
MessageStatus=delivered
To=+15551234567
From=+15559876543
MessagePrice=-0.0079
MessagePriceCurrency=USD
```

**Example Twilio Request** (failed):
```
MessageSid=SM1234567890abcdef
MessageStatus=failed
To=+15551234567
From=+15559876543
ErrorCode=30003
ErrorMessage=Phone number is unreachable
```

---

### 2. Incoming SMS Webhook

**Endpoint**: `POST /api/webhooks/twilio/incoming`

**Purpose**: Process incoming SMS replies from volunteers (YES/NO/STOP/START/HELP keywords)

**Authentication**: **None** (public webhook, validated via Twilio signature)

**Authorization**: Twilio signature validation (HMAC-SHA256)

**Request Format**: Twilio sends `application/x-www-form-urlencoded`

**Request Parameters** (Form Data):

- `MessageSid` (string): Twilio message ID for incoming SMS
- `From` (string): Sender phone number (volunteer, E.164 format)
- `To` (string): Recipient phone number (SignUpFlow Twilio number)
- `Body` (string): SMS message text (volunteer's reply)
- `NumMedia` (string): Number of media attachments (always "0" for SignUpFlow)

**Twilio Signature Validation**:
```
X-Twilio-Signature: {HMAC-SHA256 signature}
```

**Supported Keywords**:

| Keyword | Action | Response SMS |
|---------|--------|-------------|
| **YES**, **Y**, **CONFIRM** | Confirm pending assignment | "Assignment confirmed for [Event] on [Date]. See you there!" |
| **NO**, **N**, **DECLINE** | Decline pending assignment | "You have declined [Event]. Administrator has been notified." |
| **STOP**, **UNSUBSCRIBE**, **CANCEL**, **END**, **QUIT** | Opt out of SMS | "You have unsubscribed from SignUpFlow SMS notifications. Reply START to re-enable." |
| **START**, **UNSTOP** | Re-enable SMS (requires verification) | "To re-enable SMS notifications, verify your phone at [app URL]" |
| **HELP**, **INFO** | Get help information | "SignUpFlow event notifications. Reply STOP to unsubscribe. Questions? Contact [org email]" |
| **Other** | Unknown keyword | No response (log for analytics) |

**Response**:

**Success (200 OK)** - Respond with TwiML (Twilio Markup Language):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Assignment confirmed for Sunday Service on Jan 1 at 10:00AM. See you there!</Message>
</Response>
```

**Backend Processing**:
1. Validate Twilio signature
2. Parse `Body` to extract keyword (case-insensitive, strip whitespace)
3. Find volunteer by phone number in `sms_preferences` table
4. Process keyword action (see State Machine below)
5. Send response SMS via TwiML
6. Log reply in `sms_replies` table

---

## State Machine: Assignment Confirmation/Declination

### Workflow for YES/NO Replies

```
┌─────────────────────────────────────────────────────────────┐
│ Volunteer Receives Assignment SMS                            │
│ "Sunday Service - Jan 1 at 10:00AM - Role: Usher.           │
│  Reply YES to confirm, NO to decline"                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Volunteer Replies "YES"                                      │
│ POST /webhooks/twilio/incoming                               │
│ {From: "+15551234567", Body: "YES"}                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Backend Processing                                           │
│ 1. Find volunteer by phone number                            │
│ 2. Find most recent pending assignment (last 7 days)         │
│ 3. Check assignment status = 'pending'                       │
│ 4. Update status → 'confirmed'                               │
│ 5. Set confirmed_at timestamp                                │
│ 6. Log reply in sms_replies table                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Response SMS Sent                                            │
│ "Assignment confirmed for Sunday Service on Jan 1 at         │
│  10:00AM. See you there!"                                    │
└─────────────────────────────────────────────────────────────┘
```

**State Transitions**:

| Current State | Reply | New State | Action |
|---------------|-------|-----------|--------|
| `pending` | YES | `confirmed` | Set `confirmed_at`, send confirmation SMS |
| `pending` | NO | `declined` | Set `declined_at`, send decline SMS, notify admin |
| `confirmed` | YES | `confirmed` | Idempotent (no change), send "Already confirmed" SMS |
| `confirmed` | NO | `declined` | Change mind allowed, set `declined_at`, notify admin |
| `declined` | YES | `confirmed` | Change mind allowed, set `confirmed_at`, send confirmation |
| `declined` | NO | `declined` | Idempotent (no change), send "Already declined" SMS |

**Idempotency**: Duplicate replies (YES twice) do not cause errors. State machine handles gracefully.

---

## STOP Keyword Processing (Opt-Out)

### TCPA-Compliant Opt-Out

**Requirement**: STOP replies must disable SMS within 60 seconds (TCPA regulation)

**Processing Flow**:

```
┌─────────────────────────────────────────────────────────────┐
│ Volunteer Replies "STOP"                                     │
│ POST /webhooks/twilio/incoming                               │
│ {From: "+15551234567", Body: "STOP"}                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Backend Processing (< 60 seconds)                           │
│ 1. Find volunteer by phone number                            │
│ 2. Update sms_preferences:                                   │
│    - verified = FALSE                                        │
│    - opt_out_date = NOW()                                    │
│ 3. Log opt-out in audit trail                               │
│ 4. Cancel any queued messages for this volunteer            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Response SMS Sent                                            │
│ "You have unsubscribed from SignUpFlow SMS notifications.   │
│  You will receive email notifications instead.               │
│  Reply START to re-enable."                                  │
└─────────────────────────────────────────────────────────────┘
```

**TCPA-Compliant Keywords** (case-insensitive):
- STOP
- STOPALL
- UNSUBSCRIBE
- CANCEL
- END
- QUIT

All variants must be supported per TCPA requirements.

---

## START Keyword Processing (Re-Opt-In)

**Processing Flow**:

```
┌─────────────────────────────────────────────────────────────┐
│ Volunteer Replies "START" (after previously opting out)     │
│ POST /webhooks/twilio/incoming                               │
│ {From: "+15551234567", Body: "START"}                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Backend Processing                                           │
│ 1. Find volunteer by phone number                            │
│ 2. Check if previously verified                              │
│ 3. DO NOT auto-enable SMS (security)                        │
│ 4. Send re-verification instructions                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Response SMS Sent                                            │
│ "To re-enable SMS notifications, please verify your phone   │
│  number at: https://app.signupflow.io/settings/sms          │
│  Or contact your administrator for assistance."             │
└─────────────────────────────────────────────────────────────┘
```

**Security Note**: START keyword does NOT automatically re-enable SMS. Volunteer must complete verification flow again via web UI to ensure they control the phone number.

---

## HELP Keyword Processing

**Response**:
```xml
<Response>
    <Message>SignUpFlow: Volunteer event notifications. Reply STOP to unsubscribe. Questions? Email support@signupflow.io or visit signupflow.io</Message>
</Response>
```

**TCPA Requirement**: HELP keyword must provide:
1. Who is sending messages (SignUpFlow)
2. How to opt out (Reply STOP)
3. Contact information (email/website)

---

## Webhook Security

### Twilio Signature Validation

**Purpose**: Verify webhook requests actually come from Twilio (prevent spoofing)

**Implementation**:

```python
# api/utils/twilio_signature.py
from twilio.request_validator import RequestValidator

def validate_twilio_signature(request, auth_token: str) -> bool:
    """Validate that webhook request came from Twilio."""
    validator = RequestValidator(auth_token)

    # Get signature from header
    signature = request.headers.get('X-Twilio-Signature', '')

    # Get full URL (including query params)
    url = str(request.url)

    # Get POST parameters
    params = dict(request.form)

    # Validate signature
    return validator.validate(url, params, signature)

# In webhook endpoint
@router.post("/webhooks/twilio/status")
def handle_status_webhook(request: Request):
    """Process Twilio status webhook with signature validation."""
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')

    if not validate_twilio_signature(request, auth_token):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    # Process webhook...
```

**Signature Algorithm** (for reference):
1. Sort POST parameters alphabetically
2. Concatenate URL + sorted parameters
3. HMAC-SHA256 hash with Twilio auth token
4. Base64 encode result

**Example**:
```
URL: https://app.signupflow.io/api/webhooks/twilio/status
Params: MessageSid=SM123, MessageStatus=delivered
Auth Token: abc123def456

Concat: https://app.signupflow.io/api/webhooks/twilio/statusMessageSid=SM123MessageStatus=delivered
HMAC: base64(hmac_sha256("concat string", "abc123def456"))
Signature: X-Twilio-Signature: {base64 result}
```

**Security Impact**:
- ✅ Prevents attackers from spoofing delivery status
- ✅ Prevents unauthorized opt-out of volunteers
- ✅ Ensures message costs are accurate

---

## Webhook Configuration

### Twilio Console Setup

1. **Login**: https://console.twilio.com
2. **Navigate**: Phone Numbers → Active Numbers → (Select number)
3. **Messaging Configuration**:
   - **Status Callback URL**: `https://app.signupflow.io/api/webhooks/twilio/status`
   - **Incoming Message URL**: `https://app.signupflow.io/api/webhooks/twilio/incoming`
   - **HTTP Method**: POST
   - **Fallback URL**: (optional) Backup URL if primary fails

### Webhook Retry Logic

**Twilio Retry Behavior**:
- If webhook returns non-200 status, Twilio retries up to 3 times
- Retry delays: 1 minute, 5 minutes, 10 minutes
- After 3 failures, Twilio stops retrying (webhook data lost)

**Best Practice**: Always return 200 OK immediately, process asynchronously if needed:

```python
@router.post("/webhooks/twilio/status")
async def handle_status_webhook(background_tasks: BackgroundTasks, request: Request):
    """Return 200 OK immediately, process in background."""
    # Validate signature first
    if not validate_twilio_signature(request, TWILIO_AUTH_TOKEN):
        raise HTTPException(403, "Invalid signature")

    # Queue background task
    form_data = await request.form()
    background_tasks.add_task(process_status_update, dict(form_data))

    # Return 200 OK immediately
    return Response(content="<?xml version='1.0'?><Response></Response>", media_type="application/xml")
```

---

## Error Handling

### Webhook Errors

**Scenario 1: Unknown MessageSid**

**Cause**: Webhook received for message not in database (race condition or test message)

**Response**: 200 OK (acknowledge webhook to prevent retries)

**Action**: Log warning, skip processing

---

**Scenario 2: Invalid Twilio Signature**

**Cause**: Webhook request not from Twilio (spoofing attempt or misconfigured auth token)

**Response**: 403 Forbidden

**Action**: Reject request, log security event

---

**Scenario 3: Unknown Phone Number (incoming SMS)**

**Cause**: SMS from phone number not registered in system

**Response**: 200 OK + TwiML with help message

**Action**:
```xml
<Response>
    <Message>This phone number is not registered with SignUpFlow. Visit signupflow.io to sign up.</Message>
</Response>
```

---

**Scenario 4: No Pending Assignment (YES/NO reply)**

**Cause**: Volunteer replies YES/NO but has no recent pending assignments

**Response**: 200 OK + TwiML with message

**Action**:
```xml
<Response>
    <Message>No pending assignments found. Check your schedule at signupflow.io or contact your administrator.</Message>
</Response>
```

---

## Database Updates

### Status Webhook Updates

**Table**: `sms_messages`

**Updated Fields**:
- `status`: New message status (`sent`, `delivered`, `failed`, `undelivered`)
- `sent_at`: Timestamp when status changed to `sent`
- `delivered_at`: Timestamp when status changed to `delivered`
- `failed_at`: Timestamp when status changed to `failed`
- `error_message`: Error description if status = `failed`

**SQL Example**:
```sql
UPDATE sms_messages
SET
    status = 'delivered',
    delivered_at = NOW(),
    cost_cents = 79
WHERE twilio_message_sid = 'SM1234567890abcdef';
```

---

### Incoming SMS Logging

**Table**: `sms_replies`

**Inserted Fields**:
- `person_id`: Volunteer ID (from phone lookup)
- `phone_number`: Sender phone (+15551234567)
- `message_text`: Raw SMS body
- `reply_type`: Classified keyword (`yes`, `no`, `stop`, `start`, `help`, `unknown`)
- `original_message_id`: Linked assignment SMS (if YES/NO reply)
- `event_id`: Associated event (if YES/NO reply)
- `action_taken`: Action performed (`assignment_confirmed`, `assignment_declined`, `opt_out`, etc.)
- `twilio_message_sid`: Twilio incoming message ID
- `processed_at`: Processing timestamp
- `created_at`: Receipt timestamp

**SQL Example**:
```sql
INSERT INTO sms_replies (
    person_id, phone_number, message_text, reply_type,
    event_id, action_taken, twilio_message_sid, processed_at, created_at
) VALUES (
    123, '+15551234567', 'YES', 'yes',
    456, 'assignment_confirmed', 'SM9876543210fedcba', NOW(), NOW()
);
```

---

## Performance Considerations

### Webhook Response Time

**Target**: <500ms response time (return 200 OK quickly)

**Strategy**:
1. Validate signature synchronously (<50ms)
2. Queue background task for processing
3. Return 200 OK immediately
4. Process database updates asynchronously

**Why**: Twilio has 15-second timeout. Slow responses cause retries and duplicate processing.

---

### Idempotency

**Problem**: Network issues may cause duplicate webhooks (Twilio retry logic)

**Solution**: Track processed webhooks to prevent duplicate actions

**Implementation**:
```python
def process_status_update(message_sid: str, new_status: str):
    """Idempotent status update."""
    message = db.query(SmsMessage).filter(
        SmsMessage.twilio_message_sid == message_sid
    ).first()

    if not message:
        logger.warning(f"Unknown MessageSid: {message_sid}")
        return

    # Idempotent: Only update if status changed
    if message.status != new_status:
        message.status = new_status
        if new_status == 'delivered':
            message.delivered_at = datetime.utcnow()
        elif new_status == 'failed':
            message.failed_at = datetime.utcnow()
        db.commit()
```

**For Incoming SMS**:
```python
def process_incoming_reply(message_sid: str, from_number: str, body: str):
    """Idempotent reply processing."""
    # Check if already processed
    existing_reply = db.query(SmsReply).filter(
        SmsReply.twilio_message_sid == message_sid
    ).first()

    if existing_reply:
        logger.info(f"Duplicate webhook for {message_sid}, skipping")
        return existing_reply.action_taken

    # Process reply...
```

---

## Testing

### Unit Tests

```python
# tests/unit/test_twilio_webhooks.py

def test_validate_twilio_signature_valid():
    """Test that valid Twilio signature passes validation."""
    # Generate valid signature with test auth token
    # Call validate_twilio_signature()
    # Assert returns True

def test_validate_twilio_signature_invalid():
    """Test that invalid signature fails validation."""
    # Generate invalid signature
    # Call validate_twilio_signature()
    # Assert returns False

def test_process_yes_reply_confirms_assignment():
    """Test that YES reply changes assignment to confirmed."""
    # Create pending assignment
    # Process incoming SMS with Body="YES"
    # Assert assignment.status == 'confirmed'
    # Assert confirmation SMS queued

def test_process_stop_reply_opts_out():
    """Test that STOP reply disables SMS within 60 seconds."""
    start_time = datetime.utcnow()
    # Process incoming SMS with Body="STOP"
    end_time = datetime.utcnow()

    assert (end_time - start_time).total_seconds() < 60
    assert sms_preferences.verified == False
    assert sms_preferences.opt_out_date is not None
```

### Integration Tests

```python
# tests/integration/test_twilio_webhooks.py

def test_status_webhook_updates_message(client):
    """Test that status webhook updates message in database."""
    # Create message in database
    # Send POST to /webhooks/twilio/status with valid signature
    # Assert message status updated
    # Assert response is 200 OK

def test_incoming_webhook_confirms_assignment(client, db):
    """Test that incoming YES webhook updates assignment."""
    # Create pending assignment
    # Send POST to /webhooks/twilio/incoming with Body="YES"
    # Assert assignment status changed to confirmed
    # Assert response contains confirmation message in TwiML
```

### E2E Tests

```python
# tests/e2e/test_sms_workflows.py

def test_complete_assignment_confirmation_flow(page: Page):
    """Test full assignment confirmation flow via SMS simulation."""
    # Admin assigns volunteer to event
    # Simulate Twilio sending SMS (mark as sent via status webhook)
    # Simulate volunteer replying YES (incoming webhook)
    # Verify assignment status changed in database
    # Verify volunteer sees "Confirmed" in schedule UI
```

---

## Related Documentation

- **Data Model**: `../data-model.md` - sms_messages, sms_replies, sms_preferences schemas
- **SMS API**: `sms-api.md` - Message sending endpoints that trigger status webhooks
- **Preferences API**: `preferences-api.md` - STOP keyword updates preferences
- **Quick Start**: `../quickstart.md` - Webhook URL configuration in Twilio Console
- **Research**: `../research.md` - Two-way SMS reply processing decision analysis

---

**Last Updated**: 2025-10-23
**API Version**: v1
**Feature**: 019 - SMS Notification System
