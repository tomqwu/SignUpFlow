"""Webhook service for processing Stripe events.

This service handles incoming Stripe webhook events and synchronizes
subscription state between Stripe and the local database.

Supported Events:
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.payment_succeeded
    - invoice.payment_failed
    - payment_method.attached

Example Usage:
    from api.services.webhook_service import WebhookService

    webhook_service = WebhookService(db)
    result = webhook_service.process_event(stripe_event)
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from api.models import Subscription, BillingHistory
from api.logging_config import logger


class WebhookService:
    """Service for processing Stripe webhook events."""

    def __init__(self, db: Session):
        """
        Initialize webhook service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def verify_signature(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature to ensure authenticity.

        Stripe signs webhooks using webhook secret to prevent tampering.
        This method verifies the signature matches the payload.

        Args:
            payload: Raw request body (bytes)
            sig_header: Stripe-Signature header value

        Returns:
            dict: Verified Stripe event object

        Raises:
            ValueError: If payload is invalid JSON
            Exception: If signature verification fails

        Example:
            event = webhook_service.verify_signature(
                payload=request.body(),
                sig_header=request.headers['stripe-signature']
            )
        """
        import stripe
        import os

        # Get webhook secret from environment
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

        if not webhook_secret:
            logger.warning(
                "STRIPE_WEBHOOK_SECRET not configured - webhook signature verification skipped! "
                "This is INSECURE for production. Set STRIPE_WEBHOOK_SECRET environment variable."
            )
            # For development/testing: parse payload without verification
            import json
            return json.loads(payload.decode('utf-8'))

        # Verify signature and construct event
        try:
            event = stripe.Webhook.construct_event(
                payload=payload.decode('utf-8'),
                sig_header=sig_header,
                secret=webhook_secret
            )
            logger.info(f"Webhook signature verified successfully for event {event.get('id')}")
            return event

        except ValueError as e:
            # Invalid payload
            logger.error(f"Invalid webhook payload: {e}")
            raise ValueError(f"Invalid payload: {e}")

        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            logger.error(f"Webhook signature verification failed: {e}")
            raise Exception(f"Invalid signature: {e}")

    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Stripe webhook event.

        Args:
            event: Stripe event object
                {
                    "id": "evt_xxx",
                    "type": "customer.subscription.updated",
                    "data": {"object": {...}}
                }

        Returns:
            dict: Processing result
                {
                    "success": bool,
                    "event_type": str,
                    "message": str
                }

        Example:
            result = webhook_service.process_event(stripe_event)
            if result["success"]:
                print(f"Processed {result['event_type']}")
        """
        event_type = event.get("type")
        logger.info(f"Processing webhook event: {event_type}")

        try:
            # Route to appropriate handler
            if event_type == "customer.subscription.created":
                return self._handle_subscription_created(event)
            elif event_type == "customer.subscription.updated":
                return self._handle_subscription_updated(event)
            elif event_type == "customer.subscription.deleted":
                return self._handle_subscription_deleted(event)
            elif event_type == "invoice.payment_succeeded":
                return self._handle_payment_succeeded(event)
            elif event_type == "invoice.payment_failed":
                return self._handle_payment_failed(event)
            elif event_type == "payment_method.attached":
                return self._handle_payment_method_attached(event)
            else:
                logger.info(f"Unhandled event type: {event_type}")
                return {
                    "success": True,
                    "event_type": event_type,
                    "message": "Event type not handled"
                }

        except Exception as e:
            logger.error(f"Error processing webhook event {event_type}: {e}")
            return {
                "success": False,
                "event_type": event_type,
                "message": str(e)
            }

    def _handle_subscription_created(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer.subscription.created event."""
        subscription_data = event["data"]["object"]
        stripe_sub_id = subscription_data["id"]

        # Get org_id from metadata
        org_id = subscription_data["metadata"].get("org_id")
        if not org_id:
            logger.warning(f"No org_id in subscription metadata: {stripe_sub_id}")
            return {"success": False, "message": "Missing org_id in metadata"}

        # Update local subscription
        subscription = self.db.query(Subscription).filter(
            Subscription.org_id == org_id
        ).first()

        if subscription:
            subscription.stripe_subscription_id = stripe_sub_id
            subscription.status = subscription_data["status"]
            subscription.current_period_start = datetime.fromtimestamp(
                subscription_data["current_period_start"]
            )
            subscription.current_period_end = datetime.fromtimestamp(
                subscription_data["current_period_end"]
            )

            self.db.commit()

            logger.info(f"Subscription created for org {org_id}: {stripe_sub_id}")
            return {"success": True, "event_type": "subscription_created", "message": "Processed"}

        return {"success": False, "message": "Subscription not found in database"}

    def _handle_subscription_updated(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer.subscription.updated event."""
        subscription_data = event["data"]["object"]
        stripe_sub_id = subscription_data["id"]

        # Find local subscription
        subscription = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_sub_id
        ).first()

        if not subscription:
            logger.warning(f"Subscription not found: {stripe_sub_id}")
            return {"success": False, "message": "Subscription not found"}

        # Update subscription fields
        subscription.status = subscription_data["status"]
        subscription.current_period_start = datetime.fromtimestamp(
            subscription_data["current_period_start"]
        )
        subscription.current_period_end = datetime.fromtimestamp(
            subscription_data["current_period_end"]
        )
        subscription.cancel_at_period_end = subscription_data.get("cancel_at_period_end", False)

        if subscription_data.get("trial_end"):
            subscription.trial_end_date = datetime.fromtimestamp(
                subscription_data["trial_end"]
            )

        self.db.commit()

        logger.info(f"Subscription updated: {stripe_sub_id} (status: {subscription_data['status']})")
        return {"success": True, "event_type": "subscription_updated", "message": "Processed"}

    def _handle_subscription_deleted(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer.subscription.deleted event."""
        subscription_data = event["data"]["object"]
        stripe_sub_id = subscription_data["id"]

        # Find local subscription
        subscription = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_sub_id
        ).first()

        if not subscription:
            logger.warning(f"Subscription not found: {stripe_sub_id}")
            return {"success": False, "message": "Subscription not found"}

        # Revert to free plan
        subscription.status = "cancelled"
        subscription.plan_tier = "free"
        subscription.billing_cycle = None
        subscription.cancel_at_period_end = False

        self.db.commit()

        logger.info(f"Subscription deleted: {stripe_sub_id} (reverted to free)")
        return {"success": True, "event_type": "subscription_deleted", "message": "Processed"}

    def _handle_payment_succeeded(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoice.payment_succeeded event."""
        invoice = event["data"]["object"]
        customer_id = invoice["customer"]
        amount_paid = invoice["amount_paid"]  # Amount in cents

        # Find subscription by customer ID
        subscription = self.db.query(Subscription).filter(
            Subscription.stripe_customer_id == customer_id
        ).first()

        if not subscription:
            logger.warning(f"Subscription not found for customer: {customer_id}")
            return {"success": False, "message": "Subscription not found"}

        # Record billing history
        billing_record = BillingHistory(
            org_id=subscription.org_id,
            subscription_id=subscription.id,
            event_type="charge",
            amount_cents=amount_paid,
            currency=invoice.get("currency", "usd"),
            payment_status="succeeded",
            stripe_invoice_id=invoice["id"],
            invoice_pdf_url=invoice.get("invoice_pdf"),
            description=f"Payment for {subscription.plan_tier} plan",
            extra_metadata={"invoice_number": invoice.get("number")}
        )

        self.db.add(billing_record)
        self.db.commit()

        logger.info(
            f"Payment succeeded for org {subscription.org_id}: "
            f"${amount_paid/100:.2f} (invoice: {invoice['id']})"
        )
        return {"success": True, "event_type": "payment_succeeded", "message": "Processed"}

    def _handle_payment_failed(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoice.payment_failed event."""
        invoice = event["data"]["object"]
        customer_id = invoice["customer"]
        amount_due = invoice["amount_due"]

        # Find subscription by customer ID
        subscription = self.db.query(Subscription).filter(
            Subscription.stripe_customer_id == customer_id
        ).first()

        if not subscription:
            logger.warning(f"Subscription not found for customer: {customer_id}")
            return {"success": False, "message": "Subscription not found"}

        # Update subscription status
        subscription.status = "past_due"
        self.db.commit()

        # Record billing history
        billing_record = BillingHistory(
            org_id=subscription.org_id,
            subscription_id=subscription.id,
            event_type="charge",
            amount_cents=amount_due,
            currency=invoice.get("currency", "usd"),
            payment_status="failed",
            stripe_invoice_id=invoice["id"],
            description=f"Failed payment for {subscription.plan_tier} plan",
            extra_metadata={
                "invoice_number": invoice.get("number"),
                "attempt_count": invoice.get("attempt_count")
            }
        )

        self.db.add(billing_record)
        self.db.commit()

        logger.warning(
            f"Payment failed for org {subscription.org_id}: "
            f"${amount_due/100:.2f} (invoice: {invoice['id']})"
        )
        return {"success": True, "event_type": "payment_failed", "message": "Processed"}

    def _handle_payment_method_attached(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment_method.attached event."""
        payment_method = event["data"]["object"]

        logger.info(f"Payment method attached: {payment_method['id']}")
        return {"success": True, "event_type": "payment_method_attached", "message": "Processed"}
