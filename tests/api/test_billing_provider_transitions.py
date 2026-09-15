"""Local provider-fake coverage for deferred billing state transitions."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest
import stripe

from api.core.config import settings
from api.models import (
    BillingHistory,
    Organization,
    PaymentMethod,
    Person,
    ProviderEvent,
    ProviderOperation,
    Subscription,
)
from api.security import create_access_token
from api.services.billing_service import BillingService
from api.services.stripe_service import StripeService
from api.services.webhook_service import WebhookService

pytestmark = pytest.mark.no_mock_auth


def _subscription(db, *, org_id: str = "billing-a") -> Subscription:
    db.add(Organization(id=org_id, name=org_id))
    subscription = Subscription(
        org_id=org_id,
        plan_tier="starter",
        billing_cycle="monthly",
        status="trialing",
        stripe_customer_id=f"cus-{org_id}",
        stripe_subscription_id=f"sub-{org_id}",
    )
    db.add(subscription)
    db.commit()
    return subscription


def _admin_headers(db, org_id: str = "billing-a") -> dict[str, str]:
    admin_id = f"admin-{org_id}"
    db.add(
        Person(
            id=admin_id,
            org_id=org_id,
            name="Billing Admin",
            email=f"{admin_id}@example.test",
            roles=["admin"],
        )
    )
    db.commit()
    token = create_access_token({"sub": admin_id, "org_id": org_id})
    return {"Authorization": f"Bearer {token}"}


def _subscription_event(
    event_id: str,
    *,
    created: int,
    status: str,
    org_id: str = "billing-a",
    customer_id: str | None = None,
    subscription_id: str | None = None,
) -> dict:
    return {
        "id": event_id,
        "type": "customer.subscription.updated",
        "created": created,
        "data": {
            "object": {
                "id": subscription_id or f"sub-{org_id}",
                "customer": customer_id or f"cus-{org_id}",
                "status": status,
                "current_period_start": created - 100,
                "current_period_end": created + 2_500_000,
                "cancel_at_period_end": status == "canceled",
                "metadata": {"org_id": org_id, "plan_tier": "starter"},
            }
        },
    }


def _invoice_event(event_id: str, *, created: int, succeeded: bool) -> dict:
    return {
        "id": event_id,
        "type": "invoice.payment_succeeded" if succeeded else "invoice.payment_failed",
        "created": created,
        "data": {
            "object": {
                "id": "in-billing-a",
                "customer": "cus-billing-a",
                "subscription": "sub-billing-a",
                "amount_paid": 2900 if succeeded else 0,
                "amount_due": 2900,
                "currency": "usd",
                "number": "INV-0001",
                "invoice_pdf": "https://example.test/invoices/INV-0001.pdf",
                "metadata": {"org_id": "billing-a"},
            }
        },
    }


def test_signature_verification_fails_closed_without_secret(db, monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", None)

    with pytest.raises(ValueError, match="not configured"):
        WebhookService(db).verify_signature(b"{}", "signature")


def test_invalid_signature_is_rejected_without_receipt(db, monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_test")
    construct = MagicMock(side_effect=stripe.SignatureVerificationError("bad signature", "invalid"))
    monkeypatch.setattr(stripe.Webhook, "construct_event", construct)

    with pytest.raises(ValueError, match="^Invalid signature$"):
        WebhookService(db).verify_signature(b"{}", "invalid")

    assert db.query(ProviderEvent).filter(ProviderEvent.org_id.is_(None)).count() == 0


def test_foreign_provider_mapping_is_rejected_without_mutation(db):
    subscription = _subscription(db)
    _subscription(db, org_id="billing-b")
    event = _subscription_event(
        "evt-foreign",
        created=200,
        status="active",
        org_id="billing-b",
        customer_id="cus-billing-a",
        subscription_id="sub-billing-a",
    )

    result = WebhookService(db).process_event(event)

    db.refresh(subscription)
    assert result["success"] is False
    assert result["status"] == "rejected"
    assert subscription.status == "trialing"
    receipt = (
        db.query(ProviderEvent)
        .filter(
            ProviderEvent.org_id == "billing-b",
            ProviderEvent.provider_event_id == "evt-foreign",
        )
        .one()
    )
    assert receipt.status == "rejected"
    assert receipt.org_id == "billing-b"


def test_duplicate_and_out_of_order_subscription_events_do_not_regress_state(db):
    subscription = _subscription(db)
    service = WebhookService(db)
    newest = _subscription_event("evt-new", created=300, status="active")

    first = service.process_event(newest)
    duplicate = service.process_event(newest)
    stale = service.process_event(_subscription_event("evt-old", created=200, status="past_due"))

    db.refresh(subscription)
    assert first["status"] == "processed"
    assert duplicate["status"] == "duplicate"
    assert stale["status"] == "ignored"
    assert subscription.status == "active"
    assert subscription.last_provider_event_id == "evt-new"
    assert subscription.provider_state_updated_at == datetime.fromtimestamp(300, tz=UTC).replace(
        tzinfo=None
    )
    assert db.query(ProviderEvent).filter(ProviderEvent.org_id == "billing-a").count() == 2


def test_failed_invoice_can_recover_once_without_duplicate_history(db):
    subscription = _subscription(db)
    service = WebhookService(db)

    failed = service.process_event(_invoice_event("evt-failed", created=400, succeeded=False))
    recovered = service.process_event(_invoice_event("evt-paid", created=500, succeeded=True))

    db.refresh(subscription)
    history = (
        db.query(BillingHistory)
        .filter(
            BillingHistory.org_id == "billing-a",
            BillingHistory.stripe_invoice_id == "in-billing-a",
        )
        .one()
    )
    assert failed["status"] == "processed"
    assert recovered["status"] == "processed"
    assert subscription.status == "active"
    assert history.payment_status == "succeeded"
    assert history.amount_cents == 2900
    assert history.extra_metadata["last_provider_event_id"] == "evt-paid"
    assert db.query(BillingHistory).filter(BillingHistory.org_id == "billing-a").count() == 1


def test_verified_cancellation_cannot_be_undone_by_an_older_update(db):
    subscription = _subscription(db)
    service = WebhookService(db)
    deleted = _subscription_event("evt-deleted", created=900, status="canceled")
    deleted["type"] = "customer.subscription.deleted"

    cancelled = service.process_event(deleted)
    stale = service.process_event(
        _subscription_event("evt-before-delete", created=800, status="active")
    )

    db.refresh(subscription)
    assert cancelled["status"] == "processed"
    assert stale["status"] == "ignored"
    assert subscription.status == "cancelled"
    assert subscription.plan_tier == "free"


def test_expired_trial_with_only_a_local_payment_method_loses_paid_entitlement(db):
    subscription = _subscription(db)
    subscription.trial_end_date = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=1)
    db.add(
        PaymentMethod(
            org_id="billing-a",
            stripe_payment_method_id="pm-local-only",
            is_primary=True,
            is_active=True,
        )
    )
    db.commit()

    result = BillingService(db).auto_downgrade_expired_trials()

    db.refresh(subscription)
    assert result["success"] is True
    assert result["downgraded_orgs"] == ["billing-a"]
    assert subscription.plan_tier == "free"
    assert subscription.status == "active"
    assert subscription.trial_end_date is None


def test_pending_downgrade_batch_scopes_tenants_and_defers_unapproved_credit(db):
    subscription = _subscription(db)
    subscription.plan_tier = "pro"
    subscription.status = "active"
    subscription.pending_downgrade = {
        "new_plan_tier": "starter",
        "effective_date": (datetime.now(UTC).replace(tzinfo=None) - timedelta(days=1)).isoformat(),
        "credit_amount_cents": 900,
        "reason": "local test",
    }
    db.commit()

    result = BillingService(db).apply_pending_downgrades()

    db.refresh(subscription)
    assert result["success"] is True
    assert result["applied_count"] == 1
    assert result["applied_downgrades"][0]["credit_status"] == "policy_pending"
    assert subscription.plan_tier == "starter"
    assert subscription.pending_downgrade is None


def test_cancelled_subscription_batch_processes_due_row_with_tenant_scope(db, monkeypatch):
    from api.tasks import billing_tasks

    subscription = _subscription(db)
    subscription.status = "active"
    subscription.cancel_at_period_end = True
    subscription.current_period_end = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=1)
    db.commit()
    monkeypatch.setattr(settings, "BILLING_ENABLED", True)
    monkeypatch.setattr(billing_tasks, "SessionLocal", lambda: db)

    result = billing_tasks.process_cancelled_subscriptions.run()

    subscription = db.query(Subscription).filter(Subscription.org_id == "billing-a").one()
    assert result["success"] is True
    assert result["cancelled_orgs"] == ["billing-a"]
    assert subscription.status == "cancelled"
    assert subscription.plan_tier == "free"


def test_checkout_timeout_is_durable_and_same_request_is_not_retried(db, monkeypatch):
    subscription = _subscription(db)
    subscription.plan_tier = "free"
    db.commit()
    create = MagicMock(side_effect=TimeoutError("provider response was not received"))
    monkeypatch.setattr("stripe.checkout.Session.create", create)
    service = StripeService(db)
    request = {
        "org_id": "billing-a",
        "price_id": "price_starter_monthly",
        "success_url": "https://example.test/success",
        "cancel_url": "https://example.test/cancel",
        "trial_days": 14,
    }

    first = service.create_checkout_session(**request)
    replay = service.create_checkout_session(**request)

    assert first["success"] is False
    assert first["status"] == "reconciliation_required"
    assert replay == first
    create.assert_called_once()
    operation = (
        db.query(ProviderOperation)
        .filter(
            ProviderOperation.org_id == "billing-a",
            ProviderOperation.operation_type == "checkout_session.create",
        )
        .one()
    )
    assert operation.status == "reconciliation_required"
    assert operation.attempts == 1
    assert operation.last_error == "provider response was not received"


def test_successful_checkout_replay_returns_same_session_without_second_provider_call(
    db, monkeypatch
):
    subscription = _subscription(db)
    subscription.plan_tier = "free"
    db.commit()
    create = MagicMock(
        return_value=type(
            "CheckoutSession",
            (),
            {"id": "cs-created", "url": "https://checkout.example.test/cs-created"},
        )()
    )
    monkeypatch.setattr("stripe.checkout.Session.create", create)
    service = StripeService(db)
    request = {
        "org_id": "billing-a",
        "price_id": "price_starter_monthly",
        "success_url": "https://example.test/success",
        "cancel_url": "https://example.test/cancel",
        "trial_days": 14,
    }

    first = service.create_checkout_session(**request)
    replay = service.create_checkout_session(**request)

    assert replay == first
    assert first["status"] == "created"
    assert first["session_id"] == "cs-created"
    create.assert_called_once()


def test_ambiguous_event_is_retained_for_reconciliation_without_mutation(db):
    subscription = _subscription(db)
    event = _subscription_event("evt-ambiguous", created=600, status="active")
    event["data"]["object"].pop("customer")
    event["data"]["object"]["id"] = "sub-unknown"
    event["data"]["object"]["metadata"] = {}

    result = WebhookService(db).process_event(event)

    db.refresh(subscription)
    assert result["success"] is False
    assert result["status"] == "reconciliation_required"
    assert subscription.status == "trialing"
    receipt = (
        db.query(ProviderEvent)
        .filter(
            ProviderEvent.org_id.is_(None),
            ProviderEvent.provider_event_id == "evt-ambiguous",
        )
        .one()
    )
    assert receipt.status == "reconciliation_required"
    assert receipt.org_id is None


def test_unhandled_event_without_tenant_metadata_is_durably_ignored(db):
    event = {
        "id": "evt-unhandled",
        "type": "charge.refunded",
        "created": 650,
        "data": {"object": {"id": "ch-unhandled"}},
    }

    result = WebhookService(db).process_event(event)

    assert result["success"] is True
    assert result["status"] == "ignored"
    receipt = (
        db.query(ProviderEvent)
        .filter(
            ProviderEvent.org_id.is_(None),
            ProviderEvent.provider_event_id == "evt-unhandled",
        )
        .one()
    )
    assert receipt.status == "ignored"
    assert receipt.org_id is None


def test_stripe_webhook_is_mounted_only_behind_billing_gate(client, db, monkeypatch):
    _subscription(db)
    monkeypatch.setattr(settings, "BILLING_ENABLED", False)
    disabled = client.post(
        "/api/v1/webhooks/stripe",
        content=b"{}",
        headers={"stripe-signature": "test"},
    )
    assert disabled.status_code == 404
    assert disabled.json() == {"detail": "Billing is not enabled"}

    monkeypatch.setattr(settings, "BILLING_ENABLED", True)
    event = _subscription_event("evt-api", created=700, status="active")
    verify = MagicMock(return_value=event)
    monkeypatch.setattr(WebhookService, "verify_signature", verify)
    enabled = client.post(
        "/api/v1/webhooks/stripe",
        content=b"{}",
        headers={"stripe-signature": "test"},
    )
    assert enabled.status_code == 200, enabled.text
    assert enabled.json()["status"] == "processed"
    verify.assert_called_once_with(b"{}", "test")


def test_stripe_webhook_rejects_unverifiable_payload_without_receipt(client, db, monkeypatch):
    _subscription(db)
    monkeypatch.setattr(settings, "BILLING_ENABLED", True)
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", None)

    response = client.post(
        "/api/v1/webhooks/stripe",
        content=b'{"id":"evt-forged"}',
        headers={"stripe-signature": "forged"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Stripe webhook secret is not configured"}
    assert db.query(ProviderEvent).filter(ProviderEvent.org_id.is_(None)).count() == 0


@pytest.mark.parametrize(
    "output_format,content_type,expected",
    [
        ("html", "text/html", "INV-0001"),
        ("text", "text/plain", "Amount: $29.00"),
    ],
)
def test_invoice_exports_use_existing_fields_and_truthful_formats(
    client, db, monkeypatch, output_format, content_type, expected
):
    subscription = _subscription(db)
    headers = _admin_headers(db)
    record = BillingHistory(
        org_id="billing-a",
        subscription_id=subscription.id,
        event_type="charge",
        amount_cents=2900,
        currency="usd",
        payment_status="succeeded",
        stripe_invoice_id="in-billing-a",
        description="Starter subscription",
        extra_metadata={"invoice_number": "INV-0001"},
        event_timestamp=datetime(2026, 9, 15, 12, 0),
    )
    db.add(record)
    db.commit()
    monkeypatch.setattr(settings, "BILLING_ENABLED", True)

    response = client.get(
        f"/api/v1/billing/invoices/{record.id}/pdf",
        params={"format": output_format},
        headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith(content_type)
    assert expected in response.text
