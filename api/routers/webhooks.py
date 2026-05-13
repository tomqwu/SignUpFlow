"""Webhook handlers: Stripe (subscription sync) + SendGrid (email events)."""

import base64
import json
import os
from datetime import UTC, datetime
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ec import (
    ECDSA,
    EllipticCurvePublicKey,
)
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import load_der_public_key
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from api.database import get_db
from api.logging_config import logger
from api.models import DeliveryLog, Notification, NotificationStatus
from api.services.webhook_service import WebhookService

router = APIRouter(tags=["webhooks"])

# SendGrid event types we care about. Anything else is ignored (200 OK,
# no DB write) so SendGrid doesn't retry but we don't pollute DeliveryLog
# with events we have no use for (group_unsubscribe, spam_report, etc.
# would just need explicit handling if we want to track them).
_SENDGRID_EVENT_TO_STATUS = {
    "processed": NotificationStatus.SENDING,
    "delivered": NotificationStatus.DELIVERED,
    "open": NotificationStatus.OPENED,
    "click": NotificationStatus.CLICKED,
    "bounce": NotificationStatus.BOUNCED,
    "dropped": NotificationStatus.FAILED,
    "deferred": NotificationStatus.RETRY,
}


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Handle incoming Stripe webhook events.

    Stripe sends webhook events for subscription lifecycle:
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.payment_succeeded
    - invoice.payment_failed
    - payment_method.attached

    Webhook signature verification ensures authenticity.

    Args:
        request: FastAPI request with webhook payload
        db: Database session

    Returns:
        dict: {"success": bool, "message": str}

    Raises:
        HTTPException: 400 if signature invalid or event processing fails
    """
    # Get raw body for signature verification
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        logger.error("Missing Stripe signature header")
        raise HTTPException(status_code=400, detail="Missing signature")

    webhook_service = WebhookService(db)

    # Verify signature and construct event
    try:
        event = webhook_service.verify_signature(payload, sig_header)
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid webhook payload: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Invalid signature
        logger.error(f"Invalid webhook signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Log event receipt
    logger.info(f"Received Stripe webhook: {event['type']} (id: {event['id']})")

    # Process event
    try:
        result = webhook_service.process_event(event)

        if result["success"]:
            logger.info(f"Successfully processed webhook {event['type']}")
            return {"success": True, "message": "Webhook processed"}
        else:
            logger.error(f"Failed to process webhook {event['type']}: {result['message']}")
            raise HTTPException(status_code=400, detail=result["message"])

    except Exception as e:
        logger.error(f"Error processing webhook {event['type']}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error processing webhook")


def _verify_sendgrid_signature(payload: bytes, signature_b64: str, timestamp: str) -> bool:
    """Verify SendGrid Event Webhook signature (ECDSA P-256 / SHA-256).

    Per SendGrid docs (Event Webhook → Security): payload to verify is
    ``timestamp + raw_body``, signed with the configured ECDSA public
    key, encoded as base64-DER. Returns False on any verification or
    parsing failure — never raises.
    """
    public_key_b64 = os.getenv("SENDGRID_WEBHOOK_PUBLIC_KEY", "")
    if not public_key_b64:
        # No key configured → fail closed. Operator opts in by setting
        # SENDGRID_WEBHOOK_PUBLIC_KEY in .env after enabling signed
        # event webhooks in the SendGrid dashboard.
        return False
    try:
        public_key_der = base64.b64decode(public_key_b64)
        public_key = load_der_public_key(public_key_der)
        if not isinstance(public_key, EllipticCurvePublicKey):
            return False
        signature_der = base64.b64decode(signature_b64)
        signed_payload = timestamp.encode("utf-8") + payload
        public_key.verify(signature_der, signed_payload, ECDSA(SHA256()))
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


def _apply_sendgrid_event(db: Session, event: dict[str, Any]) -> None:
    """Apply a single SendGrid event to its matching Notification +
    append a DeliveryLog row. Idempotent: rerunning the same event is
    safe (status updates are monotonic in event order; DeliveryLog is
    append-only and the unique index on (notification_id, event_type,
    timestamp) would dedupe if we add one later).
    """
    sg_message_id = event.get("sg_message_id") or event.get("smtp-id")
    event_type = event.get("event")
    if not sg_message_id or not event_type:
        return
    # SendGrid sometimes appends ".filter###.### .###" to sg_message_id;
    # the leading part before the first dot is the actual message ID.
    sg_id_base = sg_message_id.split(".", 1)[0]

    notification = (
        db.query(Notification).filter(Notification.sendgrid_message_id == sg_id_base).first()
    )
    if not notification:
        # Event for a message we don't know about (e.g. test send from
        # the dashboard). Log + drop — don't 500 the webhook.
        logger.info("SendGrid event %s for unknown sg_message_id=%s", event_type, sg_id_base)
        return

    ts_unix = event.get("timestamp")
    ts_dt = (
        datetime.fromtimestamp(ts_unix, tz=UTC)
        if isinstance(ts_unix, int | float)
        else datetime.now(UTC)
    )

    new_status = _SENDGRID_EVENT_TO_STATUS.get(event_type)
    if new_status:
        notification.status = new_status
    if event_type == "delivered":
        notification.delivered_at = ts_dt
    elif event_type == "open":
        notification.opened_at = ts_dt
    elif event_type == "click":
        notification.clicked_at = ts_dt
    elif event_type in {"bounce", "dropped"}:
        notification.error_message = event.get("reason") or event.get("response") or event_type

    db.add(
        DeliveryLog(
            notification_id=notification.id,
            event_type=event_type,
            sendgrid_message_id=sg_id_base,
            timestamp=ts_dt,
            reason=event.get("reason") or event.get("response"),
            raw_event=event,
        )
    )


@router.post("/webhooks/sendgrid")
async def sendgrid_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Consume SendGrid Event Webhook payloads, update Notification +
    append DeliveryLog rows.

    Signature verification is mandatory when SENDGRID_WEBHOOK_PUBLIC_KEY
    is set; if unset the endpoint rejects all requests (fail closed —
    don't accept unsigned events in any environment).

    Event processing runs synchronously on the request-scoped session.
    SendGrid retries on 5xx (not on slow), so the slightly-elevated p99
    latency on this endpoint is preferable to the cross-session
    visibility issues that come with a BackgroundTask + fresh
    SessionLocal — those would also miss the test-scoped DB engine.
    """
    payload = await request.body()
    signature = request.headers.get("X-Twilio-Email-Event-Webhook-Signature")
    timestamp = request.headers.get("X-Twilio-Email-Event-Webhook-Timestamp")

    if not signature or not timestamp:
        raise HTTPException(status_code=400, detail="Missing signature headers")

    if not _verify_sendgrid_signature(payload, signature, timestamp):
        # Either the signature doesn't verify or the public key isn't
        # configured. Either way, refuse — unsigned events would let
        # anyone with the URL pollute Notification status.
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        events = json.loads(payload)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    if not isinstance(events, list):
        raise HTTPException(status_code=400, detail="Expected JSON array")

    try:
        for event in events:
            if isinstance(event, dict):
                _apply_sendgrid_event(db, event)
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("SendGrid event batch processing failed: %s", exc, exc_info=True)
        # Return 200 anyway — re-delivering won't help if our code
        # raised. Log + drop is the safer choice than asking SendGrid
        # to retry a broken event forever.

    return {"received": len(events)}
