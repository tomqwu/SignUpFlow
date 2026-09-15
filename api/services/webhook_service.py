"""Durable, tenant-safe processing for deferred Stripe webhook events."""

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

import stripe
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.core.config import settings
from api.logging_config import logger
from api.models import BillingHistory, Organization, ProviderEvent, Subscription, SubscriptionEvent
from api.timeutils import utcnow

_SUBSCRIPTION_EVENTS = {
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
}
_INVOICE_EVENTS = {"invoice.payment_succeeded", "invoice.payment_failed"}
_PLAN_TIERS = {"free", "starter", "pro", "enterprise"}
_BILLING_CYCLES = {"monthly", "annual"}


class WebhookService:
    """Verify and reconcile Stripe events without trusting return-page state."""

    def __init__(self, db: Session):
        self.db = db

    def verify_signature(self, payload: bytes, sig_header: str) -> dict[str, Any]:
        """Return a verified event, failing closed when no secret is configured."""
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        if not webhook_secret:
            raise ValueError("Stripe webhook secret is not configured")
        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=webhook_secret,
            )
        except ValueError as exc:
            raise ValueError(f"Invalid payload: {exc}") from exc
        except stripe.SignatureVerificationError as exc:
            raise ValueError("Invalid signature") from exc
        return dict(event)

    def process_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Persist exactly one receipt and apply a verified event transactionally."""
        event_id = event.get("id")
        event_type = event.get("type")
        created = event.get("created")
        payload_hash = self._payload_hash(event)
        if not isinstance(event_id, str) or not event_id:
            return self._result(False, "rejected", event_type, "Missing provider event ID")
        if not isinstance(event_type, str) or not event_type:
            return self._result(False, "rejected", None, "Missing provider event type")
        if not isinstance(created, int | float):
            return self._result(False, "rejected", event_type, "Missing provider timestamp")

        org_hint = self._event_org_hint(event)
        receipt_org_id = self._known_org_id(org_hint)
        existing = self._event_receipt(event_id, receipt_org_id)
        if existing:
            existing.attempts += 1
            if existing.payload_hash != payload_hash:
                existing.error = "Duplicate event ID carried a different payload"
                self.db.commit()
                return self._result(
                    False,
                    "rejected",
                    event_type,
                    "Provider event ID payload mismatch",
                )
            self.db.commit()
            return self._result(True, "duplicate", event_type, "Event already processed")

        provider_created_at = self._provider_time(created)
        receipt = ProviderEvent(
            provider="stripe",
            provider_event_id=event_id,
            org_id=receipt_org_id,
            event_type=event_type,
            provider_created_at=provider_created_at,
            payload_hash=payload_hash,
            status="received",
            attempts=1,
        )
        self.db.add(receipt)
        try:
            self.db.flush()
        except IntegrityError:
            self.db.rollback()
            return self._result(True, "duplicate", event_type, "Event already processed")

        try:
            if event_type not in _SUBSCRIPTION_EVENTS | _INVOICE_EVENTS:
                return self._finish(receipt, True, "ignored", "Event type is not handled")

            data = event.get("data")
            provider_object = data.get("object") if isinstance(data, dict) else None
            if not isinstance(provider_object, dict):
                return self._finish(
                    receipt,
                    False,
                    "reconciliation_required",
                    "Provider event object is missing",
                )

            subscription, resolution = self._resolve_subscription(event_type, provider_object)
            if subscription is None:
                status = (
                    "rejected" if resolution.startswith("mismatch:") else "reconciliation_required"
                )
                message = resolution.removeprefix("mismatch:")
                return self._finish(receipt, False, status, message)

            receipt.org_id = subscription.org_id
            if event_type in _SUBSCRIPTION_EVENTS:
                return self._apply_subscription_event(
                    receipt, subscription, provider_object, provider_created_at
                )
            if event_type in _INVOICE_EVENTS:
                return self._apply_invoice_event(
                    receipt, subscription, provider_object, provider_created_at
                )
        except Exception as exc:
            self.db.rollback()
            logger.exception(
                "Stripe provider event requires reconciliation", extra={"event_id": event_id}
            )
            return self._retain_reconciliation_receipt(
                event_id,
                event_type,
                provider_created_at,
                payload_hash,
                receipt_org_id,
                str(exc),
            )

    def _resolve_subscription(
        self, event_type: str, provider_object: dict[str, Any]
    ) -> tuple[Subscription | None, str]:
        metadata = self._provider_metadata(provider_object)
        metadata_org_id = metadata.get("org_id")
        if not isinstance(metadata_org_id, str) or not metadata_org_id:
            return None, "Provider event is missing organization metadata"
        customer_id = self._string_value(provider_object.get("customer"))
        subscription_id = (
            self._string_value(provider_object.get("id"))
            if event_type in _SUBSCRIPTION_EVENTS
            else self._invoice_subscription_id(provider_object)
        )

        subscription = (
            self.db.query(Subscription).filter(Subscription.org_id == metadata_org_id).first()
        )
        if subscription is None:
            return None, "No local subscription matches provider identities"
        if customer_id and subscription.stripe_customer_id not in {None, customer_id}:
            return None, "mismatch:Provider customer does not match local subscription"
        if subscription_id and subscription.stripe_subscription_id not in {None, subscription_id}:
            return None, "mismatch:Provider subscription does not match local subscription"
        return subscription, "matched"

    def _apply_subscription_event(
        self,
        receipt: ProviderEvent,
        subscription: Subscription,
        provider_object: dict[str, Any],
        provider_created_at: datetime,
    ) -> dict[str, Any]:
        if (
            subscription.provider_state_updated_at
            and provider_created_at <= subscription.provider_state_updated_at
        ):
            return self._finish(receipt, True, "ignored", "Older subscription state ignored")

        previous_plan = subscription.plan_tier
        event_type = receipt.event_type
        provider_status = self._string_value(provider_object.get("status"))
        if event_type == "customer.subscription.deleted":
            subscription.status = "cancelled"
            subscription.plan_tier = "free"
            subscription.billing_cycle = None
            subscription.cancel_at_period_end = False
        else:
            if not provider_status:
                return self._finish(
                    receipt,
                    False,
                    "reconciliation_required",
                    "Subscription status is missing",
                )
            subscription.status = "cancelled" if provider_status == "canceled" else provider_status
            metadata = self._provider_metadata(provider_object)
            plan_tier = metadata.get("plan_tier")
            billing_cycle = metadata.get("billing_cycle")
            if plan_tier in _PLAN_TIERS:
                subscription.plan_tier = plan_tier
            if billing_cycle in _BILLING_CYCLES:
                subscription.billing_cycle = billing_cycle
            subscription.cancel_at_period_end = bool(
                provider_object.get("cancel_at_period_end", False)
            )

        subscription.stripe_customer_id = (
            self._string_value(provider_object.get("customer")) or subscription.stripe_customer_id
        )
        subscription.stripe_subscription_id = (
            self._string_value(provider_object.get("id")) or subscription.stripe_subscription_id
        )
        subscription.current_period_start = self._optional_provider_time(
            provider_object.get("current_period_start")
        )
        subscription.current_period_end = self._optional_provider_time(
            provider_object.get("current_period_end")
        )
        subscription.trial_end_date = self._optional_provider_time(provider_object.get("trial_end"))
        subscription.provider_state_updated_at = provider_created_at
        subscription.last_provider_event_id = receipt.provider_event_id
        self.db.add(
            SubscriptionEvent(
                org_id=subscription.org_id,
                event_type=f"provider_{event_type.rsplit('.', 1)[-1]}",
                previous_plan=previous_plan,
                new_plan=subscription.plan_tier,
                notes="Applied verified Stripe subscription state",
                extra_metadata={
                    "provider": "stripe",
                    "provider_event_id": receipt.provider_event_id,
                    "provider_status": provider_status,
                },
                event_timestamp=provider_created_at,
            )
        )
        return self._finish(receipt, True, "processed", "Subscription state applied")

    def _apply_invoice_event(
        self,
        receipt: ProviderEvent,
        subscription: Subscription,
        invoice: dict[str, Any],
        provider_created_at: datetime,
    ) -> dict[str, Any]:
        invoice_id = self._string_value(invoice.get("id"))
        if not invoice_id:
            return self._finish(
                receipt,
                False,
                "reconciliation_required",
                "Invoice ID is missing",
            )
        history = (
            self.db.query(BillingHistory)
            .filter(
                BillingHistory.org_id == subscription.org_id,
                BillingHistory.stripe_invoice_id == invoice_id,
            )
            .first()
        )
        existing_metadata = (
            history.extra_metadata if history and isinstance(history.extra_metadata, dict) else {}
        )
        previous_created_at = self._parse_provider_time(
            existing_metadata.get("provider_created_at")
        )
        if previous_created_at and provider_created_at <= previous_created_at:
            return self._finish(receipt, True, "ignored", "Older invoice state ignored")

        succeeded = receipt.event_type == "invoice.payment_succeeded"
        amount = invoice.get("amount_paid") if succeeded else invoice.get("amount_due")
        amount = amount if isinstance(amount, int) else 0
        payment_status = "succeeded" if succeeded else "failed"
        metadata = {
            "invoice_number": invoice.get("number"),
            "attempt_count": invoice.get("attempt_count"),
            "plan_tier": subscription.plan_tier,
            "provider_created_at": provider_created_at.isoformat(),
            "last_provider_event_id": receipt.provider_event_id,
        }
        if history is None:
            history = BillingHistory(
                org_id=subscription.org_id,
                subscription_id=subscription.id,
                event_type="charge",
                stripe_invoice_id=invoice_id,
            )
            self.db.add(history)
        history.amount_cents = amount
        history.currency = self._string_value(invoice.get("currency")) or "usd"
        history.payment_status = payment_status
        history.invoice_pdf_url = self._string_value(invoice.get("invoice_pdf"))
        history.description = f"{payment_status.title()} payment for {subscription.plan_tier} plan"
        history.extra_metadata = metadata
        history.event_timestamp = provider_created_at

        if not subscription.provider_state_updated_at or (
            provider_created_at >= subscription.provider_state_updated_at
        ):
            if succeeded and subscription.status in {"past_due", "incomplete", "trialing"}:
                subscription.status = "active"
            elif not succeeded and subscription.status not in {"cancelled", "canceled"}:
                subscription.status = "past_due"
            subscription.provider_state_updated_at = provider_created_at
            subscription.last_provider_event_id = receipt.provider_event_id
        return self._finish(receipt, True, "processed", f"Invoice marked {payment_status}")

    def _finish(
        self,
        receipt: ProviderEvent,
        success: bool,
        status: str,
        message: str,
    ) -> dict[str, Any]:
        receipt.status = status
        receipt.outcome = {"success": success, "message": message}
        receipt.error = message if not success else None
        receipt.processed_at = utcnow()
        self.db.commit()
        return self._result(success, status, receipt.event_type, message)

    def _retain_reconciliation_receipt(
        self,
        event_id: str,
        event_type: str,
        provider_created_at: datetime,
        payload_hash: str,
        org_id: str | None,
        error: str,
    ) -> dict[str, Any]:
        receipt = self._event_receipt(event_id, org_id)
        if receipt is None:
            receipt = ProviderEvent(
                provider="stripe",
                provider_event_id=event_id,
                org_id=org_id,
                event_type=event_type,
                provider_created_at=provider_created_at,
                payload_hash=payload_hash,
                attempts=1,
                status="reconciliation_required",
            )
            self.db.add(receipt)
        receipt.status = "reconciliation_required"
        receipt.error = error
        receipt.outcome = {"success": False, "message": error}
        receipt.processed_at = utcnow()
        self.db.commit()
        return self._result(False, "reconciliation_required", event_type, error)

    def _event_receipt(self, event_id: str, org_id: str | None) -> ProviderEvent | None:
        return (
            self.db.query(ProviderEvent)
            .filter(
                ProviderEvent.provider == "stripe",
                ProviderEvent.provider_event_id == event_id,
                ProviderEvent.org_id == org_id,
            )
            .first()
        )

    def _known_org_id(self, org_id: str | None) -> str | None:
        if org_id is None:
            return None
        exists = self.db.query(Organization.id).filter(Organization.id == org_id).first()
        return org_id if exists else None

    @staticmethod
    def _event_org_hint(event: dict[str, Any]) -> str | None:
        data = event.get("data")
        provider_object = data.get("object") if isinstance(data, dict) else None
        metadata = (
            WebhookService._provider_metadata(provider_object)
            if isinstance(provider_object, dict)
            else {}
        )
        org_id = metadata.get("org_id") if isinstance(metadata, dict) else None
        return org_id if isinstance(org_id, str) and org_id else None

    @staticmethod
    def _provider_metadata(provider_object: dict[str, Any]) -> dict[str, Any]:
        direct = provider_object.get("metadata")
        if isinstance(direct, dict) and direct.get("org_id"):
            return direct
        subscription_details = provider_object.get("subscription_details")
        if isinstance(subscription_details, dict):
            nested = subscription_details.get("metadata")
            if isinstance(nested, dict):
                return nested
        parent = provider_object.get("parent")
        if isinstance(parent, dict):
            subscription_details = parent.get("subscription_details")
            if isinstance(subscription_details, dict):
                nested = subscription_details.get("metadata")
                if isinstance(nested, dict):
                    return nested
        return direct if isinstance(direct, dict) else {}

    @classmethod
    def _invoice_subscription_id(cls, invoice: dict[str, Any]) -> str | None:
        direct = cls._string_value(invoice.get("subscription"))
        if direct:
            return direct
        parent = invoice.get("parent")
        if not isinstance(parent, dict):
            return None
        details = parent.get("subscription_details")
        if not isinstance(details, dict):
            return None
        subscription = details.get("subscription")
        return cls._string_value(subscription)

    @staticmethod
    def _payload_hash(event: dict[str, Any]) -> str:
        serialized = json.dumps(event, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def _provider_time(timestamp: int | float) -> datetime:
        return datetime.fromtimestamp(timestamp, tz=UTC).replace(tzinfo=None)

    @classmethod
    def _optional_provider_time(cls, timestamp: Any) -> datetime | None:
        return cls._provider_time(timestamp) if isinstance(timestamp, int | float) else None

    @staticmethod
    def _parse_provider_time(value: Any) -> datetime | None:
        if not isinstance(value, str):
            return None
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
        return parsed.replace(tzinfo=None)

    @staticmethod
    def _string_value(value: Any) -> str | None:
        return value if isinstance(value, str) and value else None

    @staticmethod
    def _result(
        success: bool,
        status: str,
        event_type: str | None,
        message: str,
    ) -> dict[str, Any]:
        return {
            "success": success,
            "status": status,
            "event_type": event_type,
            "message": message,
        }
