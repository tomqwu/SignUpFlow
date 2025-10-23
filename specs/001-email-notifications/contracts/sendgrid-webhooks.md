# SendGrid Event Webhook Integration

**Feature**: Email Notification System
**External Service**: SendGrid Event Webhook
**Purpose**: Receive delivery status updates (delivered, opened, clicked, bounced, etc.)

## Overview

SendGrid Event Webhook allows SignUpFlow to receive real-time notifications about email delivery events. This enables accurate delivery tracking and automatic status updates in the `notifications` table.

## Webhook Configuration

### Setup in SendGrid Dashboard

1. **Navigate to**: Settings → Mail Settings → Event Webhook
2. **HTTP Post URL**: `https://api.signupflow.io/api/webhooks/sendgrid`
3. **Event Selection**: Select all events to track
   - ✅ Processed
   - ✅ Dropped
   - ✅ Delivered
   - ✅ Deferred
   - ✅ Bounce
   - ✅ Open
   - ✅ Click
   - ✅ Spam Report
   - ✅ Unsubscribe
   - ✅ Group Unsubscribe
   - ✅ Group Resubscribe
4. **Signature Verification**: Enable (provides `X-Twilio-Email-Event-Webhook-Signature` header)
5. **Event Webhook Status**: Enabled

### Environment Variables

```bash
# .env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxx
SENDGRID_WEBHOOK_SECRET=xxxxxxxxxxxxxxxxxxxx  # For signature verification
```

## Webhook Payload Format

### Event Types

SendGrid sends webhook events as JSON array with the following structure:

```json
[
  {
    "email": "volunteer@example.com",
    "timestamp": 1516299721,
    "smtp-id": "<14c5d75ce93.dfd.64b469@ismtpd-555>",
    "event": "delivered",
    "category": ["notifications"],
    "sg_event_id": "4NztHBhOTNSH-Zl8P7o3IA==",
    "sg_message_id": "14c5d75ce93.dfd.64b469.filter0001.16648.5515E0B88.0",
    "response": "250 OK",
    "attempt": "1"
  }
]
```

### Event Type Details

#### 1. Processed
Email has been received and is ready to be delivered.

```json
{
  "email": "volunteer@example.com",
  "timestamp": 1516299721,
  "event": "processed",
  "sg_message_id": "14c5d75ce93.dfd.64b469.filter0001.16648.5515E0B88.0",
  "category": ["notifications"],
  "smtp-id": "<14c5d75ce93.dfd.64b469@ismtpd-555>"
}
```

**Action**: Update notification status to `queued`.

#### 2. Delivered
Message has been successfully delivered to the receiving server.

```json
{
  "email": "volunteer@example.com",
  "timestamp": 1516299722,
  "event": "delivered",
  "sg_message_id": "14c5d75ce93.dfd.64b469.filter0001.16648.5515E0B88.0",
  "response": "250 OK",
  "smtp-id": "<14c5d75ce93.dfd.64b469@ismtpd-555>"
}
```

**Action**: Update notification status to `delivered`, set `delivered_at` timestamp.

#### 3. Open
Recipient opened the email (tracked via transparent pixel).

```json
{
  "email": "volunteer@example.com",
  "timestamp": 1516299825,
  "event": "open",
  "sg_message_id": "14c5d75ce93.dfd.64b469.filter0001.16648.5515E0B88.0",
  "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
  "ip": "192.168.1.1"
}
```

**Action**: Update notification status to `opened`, log delivery event.

#### 4. Click
Recipient clicked a link in the email.

```json
{
  "email": "volunteer@example.com",
  "timestamp": 1516299830,
  "event": "click",
  "sg_message_id": "14c5d75ce93.dfd.64b469.filter0001.16648.5515E0B88.0",
  "url": "https://signupflow.io/app/schedule",
  "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
  "ip": "192.168.1.1"
}
```

**Action**: Update notification status to `clicked`, log delivery event with URL.

#### 5. Bounce
Receiving server could not or would not accept the message.

```json
{
  "email": "bad-email@example.com",
  "timestamp": 1516299722,
  "event": "bounce",
  "sg_message_id": "14c5d75ce93.dfd.64b469.filter0001.16648.5515E0B88.0",
  "reason": "550 5.1.1 The email account that you tried to reach does not exist",
  "status": "5.1.1",
  "type": "bounce",
  "smtp-id": "<14c5d75ce93.dfd.64b469@ismtpd-555>"
}
```

**Bounce Types**:
- **Hard Bounce** (`status` starts with `5.`): Permanent failure, invalid email
- **Soft Bounce** (`status` starts with `4.`): Temporary failure, retry later

**Action**: Update notification status to `bounced`, log error message, stop retries for hard bounce.

#### 6. Dropped
SendGrid rejected the message (invalid sender, spam, etc.).

```json
{
  "email": "volunteer@example.com",
  "timestamp": 1516299721,
  "event": "dropped",
  "sg_message_id": "14c5d75ce93.dfd.64b469.filter0001.16648.5515E0B88.0",
  "reason": "Bounced Address",
  "smtp-id": "<14c5d75ce93.dfd.64b469@ismtpd-555>"
}
```

**Action**: Update notification status to `failed`, log error message, stop retries.

#### 7. Deferred
Receiving server temporarily rejected the message (will retry).

```json
{
  "email": "volunteer@example.com",
  "timestamp": 1516299722,
  "event": "deferred",
  "sg_message_id": "14c5d75ce93.dfd.64b469.filter0001.16648.5515E0B88.0",
  "response": "450 4.2.1 The user you are trying to contact is receiving mail too quickly",
  "attempt": "1",
  "smtp-id": "<14c5d75ce93.dfd.64b469@ismtpd-555>"
}
```

**Action**: Log delivery event, SendGrid will retry automatically.

#### 8. Spam Report
Recipient marked the email as spam.

```json
{
  "email": "volunteer@example.com",
  "timestamp": 1516299850,
  "event": "spamreport",
  "sg_message_id": "14c5d75ce93.dfd.64b469.filter0001.16648.5515E0B88.0"
}
```

**Action**: Update notification status to `spam`, disable future emails to this recipient.

#### 9. Unsubscribe
Recipient clicked unsubscribe link.

```json
{
  "email": "volunteer@example.com",
  "timestamp": 1516299860,
  "event": "unsubscribe",
  "sg_message_id": "14c5d75ce93.dfd.64b469.filter0001.16648.5515E0B88.0"
}
```

**Action**: Update notification status to `unsubscribed`, disable future emails to this recipient.

## Signature Verification

SendGrid signs webhook requests with HMAC-SHA256 for security.

### Verification Algorithm

```python
# api/routers/webhooks.py

import hmac
import hashlib
import base64
from fastapi import Request, HTTPException

SENDGRID_WEBHOOK_SECRET = os.getenv("SENDGRID_WEBHOOK_SECRET")

def verify_sendgrid_signature(request: Request, payload: bytes) -> bool:
    """Verify SendGrid webhook signature."""
    signature = request.headers.get("X-Twilio-Email-Event-Webhook-Signature")
    timestamp = request.headers.get("X-Twilio-Email-Event-Webhook-Timestamp")

    if not signature or not timestamp:
        return False

    # Construct verification string
    verification_string = timestamp + payload.decode('utf-8')

    # Generate expected signature
    expected_signature = hmac.new(
        SENDGRID_WEBHOOK_SECRET.encode('utf-8'),
        verification_string.encode('utf-8'),
        hashlib.sha256
    ).digest()

    # Base64 encode
    expected_signature_b64 = base64.b64encode(expected_signature).decode('utf-8')

    # Compare signatures (constant-time comparison)
    return hmac.compare_digest(signature, expected_signature_b64)
```

### Verification in Endpoint

```python
@router.post("/webhooks/sendgrid")
async def sendgrid_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle SendGrid event webhook."""
    # Read raw payload
    payload = await request.body()

    # Verify signature
    if not verify_sendgrid_signature(request, payload):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Parse JSON
    events = await request.json()

    # Process events
    processed_count = 0
    for event in events:
        process_sendgrid_event(db, event)
        processed_count += 1

    return {"processed": processed_count}
```

## Event Processing Logic

### Main Processing Function

```python
# api/services/webhook_service.py

from api.models import Notification, DeliveryLog, NotificationStatus, DeliveryEventType

def process_sendgrid_event(db: Session, event: dict):
    """Process a single SendGrid webhook event."""
    sg_message_id = event.get("sg_message_id")
    event_type = event.get("event")
    timestamp = datetime.fromtimestamp(event.get("timestamp"))

    # Find notification by SendGrid message ID
    notification = db.query(Notification)\
        .filter(Notification.sendgrid_message_id == sg_message_id)\
        .first()

    if not notification:
        # Notification not found - log warning and skip
        logger.warning(f"Notification not found for SendGrid message ID: {sg_message_id}")
        return

    # Update notification status based on event type
    if event_type == "delivered":
        notification.status = NotificationStatus.DELIVERED
        notification.delivered_at = timestamp
        log_event_type = DeliveryEventType.DELIVERED

    elif event_type == "open":
        notification.status = NotificationStatus.OPENED
        log_event_type = DeliveryEventType.OPENED

    elif event_type == "click":
        notification.status = NotificationStatus.CLICKED
        log_event_type = DeliveryEventType.CLICKED

    elif event_type == "bounce":
        notification.status = NotificationStatus.BOUNCED
        log_event_type = DeliveryEventType.BOUNCED
        # Stop retries for bounced emails
        notification.retry_count = notification.max_retries

    elif event_type == "dropped":
        notification.status = NotificationStatus.FAILED
        log_event_type = DeliveryEventType.FAILED
        # Stop retries for dropped emails
        notification.retry_count = notification.max_retries

    elif event_type == "spamreport":
        notification.status = NotificationStatus.SPAM
        log_event_type = DeliveryEventType.SPAM
        # Disable future emails to this recipient
        disable_emails_for_recipient(db, notification.recipient_id)

    elif event_type == "unsubscribe":
        notification.status = NotificationStatus.UNSUBSCRIBED
        log_event_type = DeliveryEventType.UNSUBSCRIBED
        # Disable future emails to this recipient
        disable_emails_for_recipient(db, notification.recipient_id)

    else:
        # Unknown event type - log and skip
        logger.warning(f"Unknown SendGrid event type: {event_type}")
        return

    # Save notification status update
    db.commit()

    # Log delivery event
    delivery_log = DeliveryLog(
        notification_id=notification.id,
        event_type=log_event_type,
        timestamp=timestamp,
        status_code=None,  # SendGrid doesn't provide HTTP status in webhook
        provider_response=None,
        webhook_data=event  # Store full webhook payload
    )
    db.add(delivery_log)
    db.commit()

def disable_emails_for_recipient(db: Session, person_id: str):
    """Disable all email notifications for a recipient."""
    preferences = db.query(EmailPreference)\
        .filter(EmailPreference.person_id == person_id)\
        .all()

    for pref in preferences:
        pref.frequency = EmailFrequency.DISABLED

    db.commit()
```

## Testing Webhook Integration

### Local Development Testing

Use **ngrok** to expose local server to SendGrid:

```bash
# 1. Install ngrok
brew install ngrok  # macOS
# OR download from https://ngrok.com/

# 2. Start local server
make run  # Runs on http://localhost:8000

# 3. Start ngrok tunnel
ngrok http 8000

# Output:
# Forwarding: https://abc123.ngrok.io -> http://localhost:8000

# 4. Update SendGrid webhook URL
# Set to: https://abc123.ngrok.io/api/webhooks/sendgrid
```

### Automated Testing

#### Unit Test (Signature Verification)

```python
# tests/unit/test_webhook_signature.py

def test_verify_sendgrid_signature_valid():
    """Test valid SendGrid signature verification."""
    payload = b'[{"event":"delivered","email":"test@example.com"}]'
    timestamp = "1234567890"

    # Generate valid signature
    verification_string = timestamp + payload.decode('utf-8')
    signature = hmac.new(
        SENDGRID_WEBHOOK_SECRET.encode('utf-8'),
        verification_string.encode('utf-8'),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.b64encode(signature).decode('utf-8')

    # Mock request
    request = Mock()
    request.headers = {
        "X-Twilio-Email-Event-Webhook-Signature": signature_b64,
        "X-Twilio-Email-Event-Webhook-Timestamp": timestamp
    }

    assert verify_sendgrid_signature(request, payload) is True

def test_verify_sendgrid_signature_invalid():
    """Test invalid SendGrid signature is rejected."""
    payload = b'[{"event":"delivered"}]'
    request = Mock()
    request.headers = {
        "X-Twilio-Email-Event-Webhook-Signature": "invalid_signature",
        "X-Twilio-Email-Event-Webhook-Timestamp": "1234567890"
    }

    assert verify_sendgrid_signature(request, payload) is False
```

#### Integration Test (Event Processing)

```python
# tests/integration/test_sendgrid_webhook.py

def test_webhook_delivered_event(client, db):
    """Test webhook updates notification status to delivered."""
    # Create test notification
    notification = Notification(
        org_id="org_123",
        recipient_id="person_456",
        type=NotificationType.ASSIGNMENT,
        status=NotificationStatus.SENT,
        sendgrid_message_id="test_message_123",
        template_data={}
    )
    db.add(notification)
    db.commit()

    # Send webhook event
    webhook_payload = [{
        "email": "test@example.com",
        "timestamp": 1516299722,
        "event": "delivered",
        "sg_message_id": "test_message_123",
        "response": "250 OK"
    }]

    response = client.post(
        "/api/webhooks/sendgrid",
        json=webhook_payload,
        headers=generate_valid_signature_headers(webhook_payload)
    )

    assert response.status_code == 200
    assert response.json()["processed"] == 1

    # Verify notification updated
    db.refresh(notification)
    assert notification.status == NotificationStatus.DELIVERED
    assert notification.delivered_at is not None

def test_webhook_bounce_event_stops_retries(client, db):
    """Test bounce event stops retry attempts."""
    notification = Notification(
        org_id="org_123",
        recipient_id="person_456",
        type=NotificationType.ASSIGNMENT,
        status=NotificationStatus.SENT,
        sendgrid_message_id="test_message_456",
        retry_count=1,
        max_retries=3,
        template_data={}
    )
    db.add(notification)
    db.commit()

    # Send bounce event
    webhook_payload = [{
        "email": "bad@example.com",
        "timestamp": 1516299722,
        "event": "bounce",
        "sg_message_id": "test_message_456",
        "reason": "550 5.1.1 Email address does not exist",
        "status": "5.1.1"
    }]

    response = client.post(
        "/api/webhooks/sendgrid",
        json=webhook_payload,
        headers=generate_valid_signature_headers(webhook_payload)
    )

    assert response.status_code == 200

    # Verify notification marked as bounced and retries stopped
    db.refresh(notification)
    assert notification.status == NotificationStatus.BOUNCED
    assert notification.retry_count == notification.max_retries  # Max retries reached
```

## Error Handling

### Retry Logic for Webhook Processing

```python
@celery_app.task(bind=True, max_retries=3)
def process_webhook_event_async(self, event_data: dict):
    """Process webhook event asynchronously with retry."""
    try:
        db = SessionLocal()
        process_sendgrid_event(db, event_data)
        db.close()
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

### Idempotency

SendGrid may send duplicate webhook events. Ensure idempotent processing:

```python
def process_sendgrid_event(db: Session, event: dict):
    """Process event idempotently."""
    sg_event_id = event.get("sg_event_id")

    # Check if event already processed
    existing_log = db.query(DeliveryLog)\
        .filter(DeliveryLog.webhook_data.contains({"sg_event_id": sg_event_id}))\
        .first()

    if existing_log:
        logger.info(f"Event {sg_event_id} already processed, skipping")
        return

    # Process event (rest of logic)
    # ...
```

## Monitoring & Alerting

### Metrics to Track

1. **Webhook Latency**: Time between email sent and webhook received
2. **Processing Errors**: Failed webhook processing attempts
3. **Signature Failures**: Invalid signature attempts (potential security issue)
4. **Event Volume**: Number of events received per minute/hour

### Alert Conditions

- **High bounce rate** (>5% in 24 hours) → Check email quality
- **Signature verification failures** (>10 in 1 hour) → Potential security issue
- **Webhook processing errors** (>50 in 1 hour) → System degradation

---

**Document Status**: ✅ COMPLETE
**Integration Required**: SendGrid account setup, webhook URL configuration, signature verification
**Security**: HMAC-SHA256 signature verification mandatory
**Next Steps**: Implement webhook endpoint with signature verification
