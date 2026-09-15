"""Billing authorization must precede every provider call and mutation."""

from unittest.mock import MagicMock

import pytest

from api.core.config import settings
from api.models import BillingHistory, Organization, Person, Subscription
from api.security import create_access_token
from api.services.stripe_service import StripeService

pytestmark = pytest.mark.no_mock_auth


@pytest.fixture(autouse=True)
def _enable_billing(monkeypatch):
    """Exercise the deferred implementation only through explicit opt-in."""
    monkeypatch.setattr(settings, "BILLING_ENABLED", True)


OPERATIONS = [
    ("POST", "/subscription/upgrade", {"plan_tier": "starter", "billing_cycle": "monthly"}),
    ("POST", "/subscription/trial", {"plan_tier": "starter"}),
    ("POST", "/subscription/downgrade", {"new_plan_tier": "free"}),
    ("POST", "/subscription/cancel", {}),
    ("POST", "/subscription/cancel-downgrade", None),
    ("POST", "/subscription/reactivate", None),
    ("POST", "/payment-methods", None),
    ("DELETE", "/payment-methods/pm_test", None),
    ("PUT", "/payment-methods/pm_test/primary", None),
    ("POST", "/portal", None),
    ("GET", "/payment-methods", None),
    ("GET", "/subscription", None),
    ("GET", "/history", None),
    ("GET", "/invoices/missing/pdf", None),
]


@pytest.fixture
def billing_actors(db):
    db.add_all([Organization(id="billing-a", name="A"), Organization(id="billing-b", name="B")])
    db.flush()
    actors = {}
    for identity, org_id, roles in [
        ("admin", "billing-a", ["admin"]),
        ("volunteer", "billing-a", ["volunteer"]),
        ("super_admin", "billing-a", ["super_admin"]),
        ("foreign", "billing-b", ["admin"]),
    ]:
        db.add(
            Person(
                id=identity,
                org_id=org_id,
                name=identity,
                email=f"{identity}@example.com",
                roles=roles,
            )
        )
        actors[identity] = {
            "Authorization": (f"Bearer {create_access_token({'sub': identity, 'org_id': org_id})}")
        }
    db.commit()
    return actors


@pytest.fixture
def billing_services(monkeypatch):
    services = []
    for name, module in [
        ("StripeService", "api.services.stripe_service"),
        ("BillingService", "api.services.billing_service"),
        ("UsageService", "api.services.usage_service"),
    ]:
        service = MagicMock()
        monkeypatch.setattr(f"{module}.{name}", service)
        monkeypatch.setattr(f"api.routers.billing.{name}", service)
        services.append(service)
    return services


@pytest.mark.parametrize("method,path,body", OPERATIONS)
@pytest.mark.parametrize("caller", ["anonymous", "invalid", "volunteer", "super_admin", "foreign"])
def test_billing_denies_before_services(
    client, billing_actors, billing_services, method, path, body, caller
):
    headers = billing_actors.get(caller, {})
    if caller == "invalid":
        headers = {"Authorization": "Bearer invalid"}
    response = client.request(
        method,
        f"/api/v1/billing{path}",
        headers=headers,
        params={"org_id": "billing-a", "person_id": "admin", "payment_method_id": "pm_test"},
        json={"org_id": "billing-a", **body} if body is not None else None,
    )
    expected = {401, 403}
    if caller == "foreign" and path.startswith("/invoices/"):
        expected = {404}
    assert response.status_code in expected, response.text
    for service in billing_services:
        service.assert_not_called()


def test_portal_uses_jwt_without_identity_parameter(client, billing_actors, billing_services):
    stripe = billing_services[0]
    stripe.return_value.create_billing_portal_session.return_value = {
        "success": True,
        "url": "https://example.com/portal",
    }
    response = client.post(
        "/api/v1/billing/portal", params={"org_id": "billing-a"}, headers=billing_actors["admin"]
    )
    assert response.status_code == 200, response.text
    stripe.return_value.create_billing_portal_session.assert_called_once_with("billing-a")


@pytest.mark.parametrize("caller", ["anonymous", "invalid", "volunteer"])
def test_checkout_requires_authenticated_admin(client, billing_actors, billing_services, caller):
    headers = billing_actors.get(caller, {})
    if caller == "invalid":
        headers = {"Authorization": "Bearer invalid"}
    response = client.post(
        "/api/v1/billing/subscription/checkout-success",
        headers=headers,
        params={"session_id": "cs_test", "person_id": "admin"},
    )
    assert response.status_code in {401, 403}, response.text
    for service in billing_services:
        service.assert_not_called()


def _add_subscription(db, *, customer_id: str | None = "cus_own") -> None:
    db.add(
        Subscription(
            org_id="billing-a",
            plan_tier="free",
            status="active",
            stripe_customer_id=customer_id,
        )
    )
    db.commit()


def test_checkout_rejects_foreign_session_without_entitlement_mutation(
    client, db, billing_actors, monkeypatch
):
    _add_subscription(db)
    retrieve = MagicMock(
        return_value={
            "id": "cs_foreign",
            "customer": "cus_foreign",
            "metadata": {"org_id": "billing-b"},
            "status": "complete",
            "payment_status": "paid",
        }
    )
    monkeypatch.setattr("stripe.checkout.Session.retrieve", retrieve)

    response = client.post(
        "/api/v1/billing/subscription/checkout-success",
        headers=billing_actors["admin"],
        params={"session_id": "cs_foreign"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Checkout session not found for organization"}
    retrieve.assert_called_once_with("cs_foreign")
    subscription = db.query(Subscription).filter(Subscription.org_id == "billing-a").one()
    assert subscription.plan_tier == "free"
    assert subscription.status == "active"
    assert subscription.stripe_subscription_id is None


@pytest.mark.parametrize(
    "provider_status,payment_status,expected_status,expected_success",
    [
        ("open", "unpaid", "pending", False),
        ("complete", "paid", "complete", True),
        ("complete", "no_payment_required", "complete", True),
    ],
)
def test_checkout_reports_verified_provider_state_without_granting_entitlement(
    client,
    db,
    billing_actors,
    monkeypatch,
    provider_status,
    payment_status,
    expected_status,
    expected_success,
):
    _add_subscription(db)
    retrieve = MagicMock(
        return_value={
            "id": "cs_own",
            "customer": "cus_own",
            "metadata": {"org_id": "billing-a"},
            "status": provider_status,
            "payment_status": payment_status,
        }
    )
    monkeypatch.setattr("stripe.checkout.Session.retrieve", retrieve)

    response = client.post(
        "/api/v1/billing/subscription/checkout-success",
        headers=billing_actors["admin"],
        params={"session_id": "cs_own"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is expected_success
    assert body["checkout_status"] == expected_status
    assert body["entitlement_updated"] is False
    assert body["subscription"]["plan_tier"] == "free"
    retrieve.assert_called_once_with("cs_own")
    subscription = db.query(Subscription).filter(Subscription.org_id == "billing-a").one()
    assert subscription.plan_tier == "free"
    assert subscription.status == "active"
    assert subscription.stripe_subscription_id is None


@pytest.mark.parametrize("operation", ["detach_payment_method", "set_default_payment_method"])
@pytest.mark.parametrize("customer", [None, "cus_foreign", "cus_own"])
def test_payment_method_ownership(db, billing_actors, monkeypatch, operation, customer):
    db.add(
        Subscription(
            org_id="billing-a", plan_tier="free", status="active", stripe_customer_id="cus_own"
        )
    )
    db.commit()
    retrieve = MagicMock(return_value={"customer": customer})
    detach = MagicMock()
    modify = MagicMock()
    monkeypatch.setattr("stripe.PaymentMethod.retrieve", retrieve)
    monkeypatch.setattr("stripe.PaymentMethod.detach", detach)
    monkeypatch.setattr("stripe.Customer.modify", modify)
    result = getattr(StripeService(db), operation)("billing-a", "pm_test")
    assert result["success"] is (customer == "cus_own")
    if customer != "cus_own":
        detach.assert_not_called()
        modify.assert_not_called()
    elif operation == "detach_payment_method":
        detach.assert_called_once_with("pm_test")
    else:
        modify.assert_called_once_with(
            "cus_own", invoice_settings={"default_payment_method": "pm_test"}
        )


def test_foreign_payment_method_attach_is_rejected_before_provider_mutation(
    db, billing_actors, monkeypatch
):
    _add_subscription(db, customer_id=None)
    retrieve = MagicMock(return_value={"id": "pm_foreign", "customer": "cus_foreign"})
    create_customer = MagicMock()
    attach = MagicMock()
    modify = MagicMock()
    monkeypatch.setattr("stripe.PaymentMethod.retrieve", retrieve)
    monkeypatch.setattr("stripe.Customer.create", create_customer)
    monkeypatch.setattr("stripe.PaymentMethod.attach", attach)
    monkeypatch.setattr("stripe.Customer.modify", modify)

    result = StripeService(db).attach_payment_method("billing-a", "pm_foreign")

    assert result == {
        "success": False,
        "message": "Payment method not available for organization",
    }
    retrieve.assert_called_once_with("pm_foreign")
    create_customer.assert_not_called()
    attach.assert_not_called()
    modify.assert_not_called()
    subscription = db.query(Subscription).filter(Subscription.org_id == "billing-a").one()
    assert subscription.stripe_customer_id is None


def test_already_owned_payment_method_attach_is_idempotent(db, billing_actors, monkeypatch):
    _add_subscription(db)
    retrieve_payment_method = MagicMock(return_value={"id": "pm_own", "customer": "cus_own"})
    attach = MagicMock()
    customer = MagicMock()
    customer.invoice_settings.default_payment_method = "pm_own"
    retrieve_customer = MagicMock(return_value=customer)
    modify = MagicMock()
    monkeypatch.setattr("stripe.PaymentMethod.retrieve", retrieve_payment_method)
    monkeypatch.setattr("stripe.PaymentMethod.attach", attach)
    monkeypatch.setattr("stripe.Customer.retrieve", retrieve_customer)
    monkeypatch.setattr("stripe.Customer.modify", modify)

    result = StripeService(db).attach_payment_method("billing-a", "pm_own")

    assert result == {"success": True, "message": "Payment method added successfully"}
    retrieve_payment_method.assert_called_once_with("pm_own")
    attach.assert_not_called()
    retrieve_customer.assert_called_once_with("cus_own")
    modify.assert_not_called()


def test_existing_foreign_invoice_is_hidden(client, db, billing_actors):
    db.add(
        BillingHistory(id=101, org_id="billing-b", event_type="charge", payment_status="succeeded")
    )
    db.commit()
    response = client.get("/api/v1/billing/invoices/101/pdf", headers=billing_actors["admin"])
    assert response.status_code == 404
    assert response.json() == {"detail": "Invoice not found"}
