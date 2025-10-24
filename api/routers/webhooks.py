"""Stripe webhook handlers for real-time subscription synchronization."""

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from api.database import get_db
from api.services.webhook_service import WebhookService
from api.logging_config import logger

router = APIRouter(tags=["webhooks"])


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
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
    sig_header = request.headers.get('stripe-signature')

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
