"""Commercial integrations stay outside the active business workflow."""

from unittest.mock import MagicMock

from api.core.config import settings
from api.models import Subscription
from tests.api.conftest import auth_headers, seed_org, seed_user


def test_billing_is_unavailable_before_provider_construction(client, db, monkeypatch):
    monkeypatch.setattr(settings, "BILLING_ENABLED", False)
    stripe_service = MagicMock()
    billing_service = MagicMock()
    monkeypatch.setattr("api.routers.billing.StripeService", stripe_service)
    monkeypatch.setattr("api.routers.billing.BillingService", billing_service)

    seed_org(client, "commercial-off")
    seed_user(
        client,
        "commercial-off",
        email="admin@commercial-off.example.com",
        name="Admin",
        password="AdminPass1!",
    )
    headers = auth_headers(client, "admin@commercial-off.example.com", "AdminPass1!")

    response = client.get(
        "/api/v1/billing/subscription?org_id=commercial-off",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Billing is not enabled"}
    stripe_service.assert_not_called()
    billing_service.assert_not_called()
    assert db.query(Subscription).count() == 0


def test_sms_is_unavailable_before_provider_construction(client, monkeypatch):
    monkeypatch.setattr(settings, "SMS_ENABLED", False)
    sms_service = MagicMock()
    monkeypatch.setattr("api.routers.sms.SMSService", sms_service)

    response = client.post(
        "/api/sms/verify-phone",
        headers={"Authorization": "Bearer invalid"},
        json={"phone_number": "+14165550123"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "SMS is not enabled"}
    sms_service.assert_not_called()


def test_billing_task_is_disabled_before_database_or_service(monkeypatch):
    from api.tasks import billing_tasks

    monkeypatch.setattr(settings, "BILLING_ENABLED", False)
    session = MagicMock()
    service = MagicMock()
    monkeypatch.setattr(billing_tasks, "SessionLocal", session)
    monkeypatch.setattr(billing_tasks, "BillingService", service)

    result = billing_tasks.check_expired_trials.run()

    assert result == {
        "success": False,
        "status": "disabled",
        "message": "Billing is not enabled",
    }
    session.assert_not_called()
    service.assert_not_called()


def test_sms_task_is_disabled_before_database_or_service(monkeypatch):
    from api.tasks import sms_tasks

    monkeypatch.setattr(settings, "SMS_ENABLED", False)
    session = MagicMock()
    service = MagicMock()
    monkeypatch.setattr(sms_tasks, "SessionLocal", session)
    monkeypatch.setattr(sms_tasks, "SMSService", service)

    result = sms_tasks.send_assignment_notification.run(1, "event-1", "person-1", 1)

    assert result == {"status": "disabled", "message": "SMS is not enabled"}
    session.assert_not_called()
    service.assert_not_called()
