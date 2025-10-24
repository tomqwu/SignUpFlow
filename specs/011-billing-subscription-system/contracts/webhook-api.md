# API Contract: Stripe Webhooks

**Feature**: 011-billing-subscription-system
**Router**: `api/routers/webhooks.py`
**Base Path**: `/api/webhooks`
**Date**: 2025-10-22

## Overview

Stripe webhook endpoint for processing subscription lifecycle events. Webhooks provide reliable, asynchronous notification of subscription changes, payment events, and customer updates.

---

## Authentication

**Webhook Signature Verification**:
- Uses Stripe webhook signing secret (`STRIPE_WEBHOOK_SECRET`)
- Validates `Stripe-Signature` header to prevent spoofing
- Rejects requests with invalid/missing signatures

**No JWT Required**: Webhooks authenticated via Stripe signature only

---

## Endpoint

### Process Stripe Webhook

**Purpose**: Receive and process Stripe webhook events

**Endpoint**: `POST /api/webhooks/stripe`

**Headers**:
```
Stripe-Signature: t=1492774577,v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd
Content-Type: application/json
```

**Request Body** (Stripe Event Format):
```json
{
  "id": "evt_1OQz8xJ2eZvKYlo2",
  "object": "event",
  "type": "customer.subscription.updated",
  "created": 1642694400,
  "data": {
    "object": {
      "id": "sub_1OQz8xJ2eZvKYlo2",
      "customer": "cus_NQz8xY2I4rXVqP",
      "status": "active",
      "items": {
        "data": [{
          "price": {
            "id": "price_1OQz8xJ2eZvKYlo2"
          }
        }]
      },
      "current_period_start": 1642694400,
      "current_period_end": 1674230400,
      "trial_end": null,
      "cancel_at_period_end": false
    }
  }
}
```

**Response 200 OK** (Immediate acknowledgment):
```json
{
  "status": "received",
  "event_id": "evt_1OQz8xJ2eZvKYlo2"
}
```

**Response 400 Bad Request** (Invalid signature):
```json
{
  "error": "invalid_signature",
  "message": "Webhook signature verification failed"
}
```

**Business Logic**:
1. **Verify Signature**: Validate `Stripe-Signature` header using webhook secret
2. **Queue Event**: Add event to Celery queue for async processing (return 200 immediately)
3. **Process Async**: Handle event in background worker
4. **Idempotency**: Check if event already processed (by `event_id`)
5. **Update Database**: Sync local subscription status with Stripe data

---

## Supported Webhook Events

### 1. customer.subscription.created

**When Triggered**: New subscription created (user upgrades from Free to paid plan or starts trial)

**Event Data**:
```json
{
  "type": "customer.subscription.created",
  "data": {
    "object": {
      "id": "sub_1OQz8xJ2eZvKYlo2",
      "customer": "cus_NQz8xY2I4rXVqP",
      "status": "active",
      "metadata": {"org_id": "org_church_xyz"},
      "trial_end": null
    }
  }
}
```

**Processing Logic**:
```python
def handle_subscription_created(event_data):
    subscription_data = event_data["object"]
    org_id = subscription_data["metadata"]["org_id"]

    # Update local subscription record
    update_subscription_from_stripe(org_id, subscription_data)

    # Send confirmation email
    email_service.send_subscription_confirmation(org_id, subscription_data)

    # Log audit event
    SubscriptionEvent.create(
        org_id=org_id,
        event_type="created",
        new_plan=subscription_data["plan_tier"]
    )
```

---

### 2. customer.subscription.updated

**When Triggered**: Subscription modified (plan change, status change, renewal)

**Event Data**:
```json
{
  "type": "customer.subscription.updated",
  "data": {
    "object": {
      "id": "sub_1OQz8xJ2eZvKYlo2",
      "status": "active",
      "cancel_at_period_end": false
    },
    "previous_attributes": {
      "status": "past_due"
    }
  }
}
```

**Processing Logic**:
```python
def handle_subscription_updated(event_data):
    subscription_data = event_data["object"]
    previous = event_data.get("previous_attributes", {})
    org_id = subscription_data["metadata"]["org_id"]

    # Detect what changed
    if "status" in previous:
        # Status change (e.g., past_due → active after payment recovery)
        handle_status_change(org_id, previous["status"], subscription_data["status"])

    if "items" in previous:
        # Plan upgrade/downgrade
        handle_plan_change(org_id, subscription_data)

    # Update local database
    update_subscription_from_stripe(org_id, subscription_data)
```

**Status Transitions**:
- `trialing → active`: Trial converted to paid (payment successful)
- `trialing → canceled`: Trial expired without payment
- `past_due → active`: Failed payment recovered
- `active → past_due`: Payment failure (retry in progress)
- `active → canceled`: Cancellation effective

---

### 3. customer.subscription.deleted

**When Triggered**: Subscription cancelled and period ended (or immediately cancelled)

**Event Data**:
```json
{
  "type": "customer.subscription.deleted",
  "data": {
    "object": {
      "id": "sub_1OQz8xJ2eZvKYlo2",
      "customer": "cus_NQz8xY2I4rXVqP",
      "status": "canceled",
      "ended_at": 1674230400
    }
  }
}
```

**Processing Logic**:
```python
def handle_subscription_deleted(event_data):
    subscription_data = event_data["object"]
    org_id = subscription_data["metadata"]["org_id"]

    # Downgrade to Free plan
    downgrade_to_free_plan(org_id)

    # Start data retention countdown
    set_data_retention_period(org_id, days=30)

    # Send cancellation confirmation email
    email_service.send_subscription_cancelled(org_id)

    # Log audit event
    SubscriptionEvent.create(
        org_id=org_id,
        event_type="downgraded",
        previous_plan=subscription_data["plan_tier"],
        new_plan="free",
        reason="subscription_ended"
    )
```

---

### 4. customer.subscription.trial_will_end

**When Triggered**: 3 days before trial expires

**Event Data**:
```json
{
  "type": "customer.subscription.trial_will_end",
  "data": {
    "object": {
      "id": "sub_1OQz8xJ2eZvKYlo2",
      "trial_end": 1642954800
    }
  }
}
```

**Processing Logic**:
```python
def handle_trial_ending_soon(event_data):
    subscription_data = event_data["object"]
    org_id = subscription_data["metadata"]["org_id"]
    trial_end_date = datetime.fromtimestamp(subscription_data["trial_end"])
    days_remaining = (trial_end_date - datetime.utcnow()).days

    # Send reminder email
    email_service.send_trial_ending_soon(org_id, days_remaining)
```

---

### 5. invoice.payment_succeeded

**When Triggered**: Subscription payment successful (renewal, upgrade prorated charge)

**Event Data**:
```json
{
  "type": "invoice.payment_succeeded",
  "data": {
    "object": {
      "id": "in_1OQz8xJ2eZvKYlo2",
      "customer": "cus_NQz8xY2I4rXVqP",
      "amount_paid": 7900,
      "currency": "usd",
      "hosted_invoice_url": "https://pay.stripe.com/invoice/...",
      "invoice_pdf": "https://pay.stripe.com/invoice/.../pdf",
      "subscription": "sub_1OQz8xJ2eZvKYlo2"
    }
  }
}
```

**Processing Logic**:
```python
def handle_payment_succeeded(event_data):
    invoice = event_data["object"]
    org_id = get_org_id_from_stripe_customer(invoice["customer"])

    # Record billing history
    BillingHistory.create(
        org_id=org_id,
        event_type="charge",
        amount_cents=invoice["amount_paid"],
        currency=invoice["currency"],
        payment_status="succeeded",
        stripe_invoice_id=invoice["id"],
        invoice_pdf_url=invoice["invoice_pdf"],
        description=f"Payment for {invoice['description']}"
    )

    # Send invoice email
    email_service.send_invoice(org_id, invoice)
```

---

### 6. invoice.payment_failed

**When Triggered**: Subscription payment failed (expired card, insufficient funds, etc.)

**Event Data**:
```json
{
  "type": "invoice.payment_failed",
  "data": {
    "object": {
      "id": "in_1OQz8xJ2eZvKYlo2",
      "customer": "cus_NQz8xY2I4rXVqP",
      "amount_due": 7900,
      "attempt_count": 1,
      "next_payment_attempt": 1643040000,
      "last_payment_error": {
        "message": "Your card was declined."
      }
    }
  }
}
```

**Processing Logic**:
```python
def handle_payment_failed(event_data):
    invoice = event_data["object"]
    org_id = get_org_id_from_stripe_customer(invoice["customer"])

    # Record failed payment
    BillingHistory.create(
        org_id=org_id,
        event_type="charge",
        amount_cents=invoice["amount_due"],
        payment_status="failed",
        description=f"Payment failed: {invoice['last_payment_error']['message']}"
    )

    # Update subscription status to past_due
    update_subscription_status(org_id, "past_due")

    # Send failure notification (immediate)
    email_service.send_payment_failed(org_id, invoice)

    # Schedule warning emails
    if invoice["attempt_count"] == 1:
        schedule_payment_retry_warnings(org_id, invoice)
```

**Retry Schedule** (Stripe Smart Retries):
- Attempt 1: Immediate failure notification
- Attempt 2: 3 days later (warning email)
- Attempt 3: 5 days after attempt 2 (final warning)
- Attempt 4: 7 days after attempt 3 (last chance)
- After 4 failures: Subscription cancelled, downgrade to Free

---

### 7. payment_method.attached

**When Triggered**: Customer adds payment method to their account

**Event Data**:
```json
{
  "type": "payment_method.attached",
  "data": {
    "object": {
      "id": "pm_1OQz8xJ2eZvKYlo2",
      "customer": "cus_NQz8xY2I4rXVqP",
      "card": {
        "brand": "visa",
        "last4": "4242",
        "exp_month": 12,
        "exp_year": 2027
      }
    }
  }
}
```

**Processing Logic**:
```python
def handle_payment_method_attached(event_data):
    payment_method = event_data["object"]
    org_id = get_org_id_from_stripe_customer(payment_method["customer"])

    # Store payment method metadata
    PaymentMethod.create(
        org_id=org_id,
        stripe_payment_method_id=payment_method["id"],
        card_brand=payment_method["card"]["brand"],
        card_last4=payment_method["card"]["last4"],
        exp_month=payment_method["card"]["exp_month"],
        exp_year=payment_method["card"]["exp_year"],
        is_primary=True
    )
```

---

### 8. payment_method.detached

**When Triggered**: Customer removes payment method

**Event Data**:
```json
{
  "type": "payment_method.detached",
  "data": {
    "object": {
      "id": "pm_1OQz8xJ2eZvKYlo2"
    }
  }
}
```

**Processing Logic**:
```python
def handle_payment_method_detached(event_data):
    payment_method = event_data["object"]

    # Mark as inactive (soft delete)
    pm = PaymentMethod.query.filter_by(
        stripe_payment_method_id=payment_method["id"]
    ).first()
    if pm:
        pm.is_active = False
        db.session.commit()
```

---

## Event Processing Architecture

### Queue-Based Processing

**Why Async**:
1. Stripe expects 200 response within 5 seconds
2. Database operations may take longer (multi-tenant queries, writes)
3. Email sending is slow (SMTP, external API calls)
4. Retry logic easier with queue system

**Architecture**:
```
Stripe → POST /webhooks/stripe
         ↓
    [Verify Signature] (fast, <100ms)
         ↓
    [Queue Event] (fast, <50ms)
         ↓
    [Return 200 OK] (fast, <150ms total)
         ↓
    Celery Worker (async, 1-30s)
         ↓
    [Process Event]
    [Update Database]
    [Send Emails]
    [Log Audit]
```

**Implementation**:
```python
# api/routers/webhooks.py
@router.post("/stripe")
async def stripe_webhook(request: Request):
    # 1. Get raw body and signature
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # 2. Verify signature (CRITICAL - prevents spoofing)
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 3. Queue for async processing (fast return)
    process_stripe_event.delay(event["id"], event["type"], event["data"])

    # 4. Return 200 immediately (Stripe requirement)
    return {"status": "received", "event_id": event["id"]}


# api/tasks/webhook_tasks.py
@celery_app.task(bind=True, max_retries=5)
def process_stripe_event(self, event_id, event_type, event_data):
    """Process Stripe webhook event with retry logic"""
    try:
        # Idempotency check
        if WebhookEvent.query.filter_by(stripe_event_id=event_id).first():
            logger.info(f"Event {event_id} already processed, skipping")
            return {"status": "already_processed"}

        # Route to appropriate handler
        handler = EVENT_HANDLERS.get(event_type)
        if handler:
            handler(event_data)
        else:
            logger.warning(f"Unhandled event type: {event_type}")

        # Mark as processed
        WebhookEvent.create(stripe_event_id=event_id, processed=True, event_type=event_type)

    except Exception as exc:
        logger.error(f"Failed to process event {event_id}: {exc}")
        # Retry with exponential backoff: 4s, 16s, 64s, 256s, 1024s
        raise self.retry(exc=exc, countdown=4 ** self.request.retries)
```

### Idempotency

**Why Needed**: Stripe may send same event multiple times (network failures, retries)

**Implementation**:
```python
class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    stripe_event_id = Column(String, primary_key=True)  # Unique constraint
    event_type = Column(String, nullable=False)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True))
    retry_count = Column(Integer, default=0)
```

**Check Before Processing**:
```python
if WebhookEvent.query.filter_by(stripe_event_id=event_id).first():
    return {"status": "already_processed"}
```

---

## Fallback Polling

**Purpose**: If webhooks fail (network issues, server downtime), polling ensures eventual consistency

**Implementation**:
```python
# api/tasks/billing_tasks.py
@celery_app.task
def sync_stripe_subscriptions():
    """
    Fallback mechanism: Poll Stripe API every 6 hours to sync subscriptions
    Only needed if webhooks are delayed/failed
    """
    for org in Organization.query.filter(Organization.stripe_subscription_id.isnot(None)):
        try:
            # Fetch latest from Stripe
            stripe_sub = stripe.Subscription.retrieve(org.stripe_subscription_id)

            # Compare with local
            local_sub = org.subscription
            if local_sub.status != stripe_sub.status:
                logger.warning(f"Subscription {stripe_sub.id} out of sync, updating")
                update_subscription_from_stripe(org.id, stripe_sub)

        except stripe.error.InvalidRequestError:
            # Subscription deleted in Stripe but not locally
            logger.error(f"Subscription {org.stripe_subscription_id} not found in Stripe")
            handle_subscription_deleted_fallback(org.id)

# Schedule: Every 6 hours
celery_app.conf.beat_schedule = {
    "sync-stripe-subscriptions": {
        "task": "api.tasks.billing_tasks.sync_stripe_subscriptions",
        "schedule": crontab(minute=0, hour="*/6")  # Every 6 hours
    }
}
```

---

## Error Handling

### Webhook Processing Failures

**Retry Logic**:
- Celery retries 5 times with exponential backoff
- Backoff: 4s, 16s, 64s, 256s (4m), 1024s (17m)
- After 5 failures: Alert admin via error tracking (Sentry)

**Dead Letter Queue**:
```python
@celery_app.task(bind=True, max_retries=5)
def process_stripe_event(self, event_id, event_type, event_data):
    try:
        # ... processing
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            # Send to dead letter queue
            FailedWebhookEvent.create(
                event_id=event_id,
                event_type=event_type,
                failure_reason=str(exc),
                retry_count=self.request.retries
            )
            # Alert admin
            notify_webhook_failure(event_id, event_type, exc)
        else:
            # Retry
            raise self.retry(exc=exc, countdown=4 ** self.request.retries)
```

---

## Testing

### Local Testing with Stripe CLI

**Setup**:
```bash
# Install Stripe CLI
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

**Trigger Test Events**:
```bash
# Subscription created
stripe trigger customer.subscription.created

# Payment failed
stripe trigger invoice.payment_failed

# Trial ending
stripe trigger customer.subscription.trial_will_end

# Custom event
stripe trigger customer.subscription.updated --add customer:metadata.org_id=org_test_123
```

### E2E Webhook Tests

```python
# tests/integration/test_webhook_processing.py
def test_subscription_created_webhook():
    """Test webhook processing for subscription creation"""
    # Construct webhook payload
    event = {
        "id": "evt_test_123",
        "type": "customer.subscription.created",
        "data": {
            "object": {
                "id": "sub_test_123",
                "customer": "cus_test_123",
                "status": "active",
                "metadata": {"org_id": "org_test"}
            }
        }
    }

    # Generate valid signature
    timestamp = int(time.time())
    signature = generate_stripe_signature(json.dumps(event), timestamp)

    # Send webhook request
    response = client.post(
        "/api/webhooks/stripe",
        json=event,
        headers={"Stripe-Signature": f"t={timestamp},v1={signature}"}
    )

    # Verify immediate response
    assert response.status_code == 200
    assert response.json()["status"] == "received"

    # Wait for async processing
    time.sleep(2)

    # Verify database updated
    org = db.query(Organization).filter_by(id="org_test").first()
    assert org.subscription.status == "active"
    assert org.subscription.stripe_subscription_id == "sub_test_123"
```

---

## Security

### Signature Verification

**Critical**: Always verify webhook signatures to prevent spoofing

```python
# CORRECT - Verify signature
event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)

# WRONG - Skip verification (SECURITY VULNERABILITY!)
event = json.loads(payload)  # ❌ Anyone can send fake webhooks!
```

### IP Allowlisting (Optional)

Stripe webhook IPs (for additional security):
- Not required (signature verification is sufficient)
- Can add as defense-in-depth layer
- Stripe IP ranges published at: https://stripe.com/docs/ips

---

## Monitoring

### Webhook Health Metrics

**Track**:
- Webhook processing latency
- Failed webhook count
- Retry rate
- Dead letter queue size

**Alerts**:
- Alert if webhook delay >5 minutes (indicates processing backlog)
- Alert if retry rate >10% (indicates recurring failures)
- Alert if dead letter queue grows (requires manual intervention)

**Dashboard**:
```python
# Admin dashboard query
webhook_stats = {
    "total_processed_today": WebhookEvent.query.filter(
        WebhookEvent.processed_at >= datetime.utcnow() - timedelta(days=1)
    ).count(),
    "failed_last_hour": FailedWebhookEvent.query.filter(
        FailedWebhookEvent.created_at >= datetime.utcnow() - timedelta(hours=1)
    ).count(),
    "average_processing_time_seconds": db.session.query(
        func.avg(WebhookEvent.processing_duration)
    ).scalar()
}
```

---

**Webhook Contract Version**: 1.0
**Last Updated**: 2025-10-22
**Status**: Ready for Implementation
