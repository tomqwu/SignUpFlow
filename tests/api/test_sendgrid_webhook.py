"""Tenant-safe, provider-free SendGrid Event Webhook tests."""

import json

from api.core.config import settings
from api.models import (
    DeliveryLog,
    Notification,
    NotificationStatus,
    Organization,
    Person,
    ProviderEvent,
)
from api.routers import webhooks


def _notification(db, *, org_id: str, message_id: str) -> Notification:
    db.add(Organization(id=org_id, name=org_id))
    db.add(
        Person(
            id=f"{org_id}-person",
            org_id=org_id,
            name="Volunteer",
            email=f"{org_id}@example.test",
            roles=["volunteer"],
        )
    )
    db.flush()
    notification = Notification(
        org_id=org_id,
        recipient_id=f"{org_id}-person",
        type="assignment",
        status=NotificationStatus.SENT,
        sendgrid_message_id=message_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def _event(notification: Notification, **overrides) -> dict[str, object]:
    event: dict[str, object] = {
        "event": "delivered",
        "timestamp": 1_800_000_000,
        "sg_message_id": f"{notification.sendgrid_message_id}.filter001",
        "sg_event_id": "sg-event-1",
        "signupflow_org_id": notification.org_id,
        "signupflow_notification_id": str(notification.id),
    }
    event.update(overrides)
    return event


def _post(client, events: list[dict[str, object]]):
    return client.post(
        "/api/v1/webhooks/sendgrid",
        content=json.dumps(events).encode(),
        headers={
            "X-Twilio-Email-Event-Webhook-Signature": "verified-locally",
            "X-Twilio-Email-Event-Webhook-Timestamp": "1800000000",
        },
    )


def test_sendgrid_webhook_is_mounted_only_behind_email_gate(client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "EMAIL_ENABLED", False)

    response = _post(client, [])

    assert response.status_code == 404
    assert response.json() == {"detail": "Email is not enabled"}


def test_sendgrid_webhook_rejects_invalid_signature_without_receipt(
    client, db, monkeypatch
) -> None:
    monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
    monkeypatch.setattr(webhooks, "_verify_sendgrid_signature", lambda *_args: False)

    response = _post(client, [{"event": "delivered"}])

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid signature"}
    assert db.query(DeliveryLog).count() == 0
    assert db.query(ProviderEvent).filter(ProviderEvent.org_id.is_(None)).count() == 0


def test_sendgrid_webhook_applies_matching_event_once(client, db, monkeypatch) -> None:
    notification = _notification(db, org_id="church-east", message_id="sg-message-1")
    monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
    monkeypatch.setattr(webhooks, "_verify_sendgrid_signature", lambda *_args: True)

    first = _post(client, [_event(notification)])
    second = _post(client, [_event(notification)])

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    db.expire_all()
    persisted = (
        db.query(Notification)
        .filter(
            Notification.id == notification.id,
            Notification.org_id == "church-east",
        )
        .one()
    )
    assert persisted.status == NotificationStatus.DELIVERED
    assert (
        db.query(DeliveryLog)
        .filter(
            DeliveryLog.notification_id == notification.id,
        )
        .count()
        == 1
    )
    receipt = (
        db.query(ProviderEvent)
        .filter(
            ProviderEvent.provider == "sendgrid",
            ProviderEvent.provider_event_id == "sg-event-1",
            ProviderEvent.org_id == "church-east",
        )
        .one()
    )
    assert receipt.status == "processed"
    assert receipt.attempts == 2


def test_sendgrid_webhook_rejects_cross_tenant_metadata_without_mutation(
    client, db, monkeypatch
) -> None:
    notification = _notification(db, org_id="church-east", message_id="sg-message-1")
    db.add(Organization(id="basketball-west", name="Basketball West"))
    db.commit()
    monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
    monkeypatch.setattr(webhooks, "_verify_sendgrid_signature", lambda *_args: True)

    response = _post(
        client,
        [
            _event(
                notification,
                sg_event_id="sg-event-cross-tenant",
                signupflow_org_id="basketball-west",
            )
        ],
    )

    assert response.status_code == 200, response.text
    db.expire_all()
    persisted = (
        db.query(Notification)
        .filter(
            Notification.id == notification.id,
            Notification.org_id == "church-east",
        )
        .one()
    )
    assert persisted.status == NotificationStatus.SENT
    assert db.query(DeliveryLog).count() == 0
    assert (
        db.query(ProviderEvent)
        .filter(
            ProviderEvent.provider == "sendgrid",
            ProviderEvent.provider_event_id == "sg-event-cross-tenant",
            ProviderEvent.org_id == "basketball-west",
        )
        .one()
        .status
        == "reconciliation_required"
    )


def test_sendgrid_webhook_ignores_event_without_tenant_metadata(client, db, monkeypatch) -> None:
    notification = _notification(db, org_id="church-east", message_id="sg-message-1")
    monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
    monkeypatch.setattr(webhooks, "_verify_sendgrid_signature", lambda *_args: True)

    response = _post(
        client,
        [_event(notification, signupflow_org_id=None, signupflow_notification_id=None)],
    )

    assert response.status_code == 200, response.text
    db.expire_all()
    assert (
        db.query(Notification)
        .filter(
            Notification.id == notification.id,
            Notification.org_id == "church-east",
        )
        .one()
        .status
        == NotificationStatus.SENT
    )
    assert db.query(DeliveryLog).count() == 0
    assert (
        db.query(ProviderEvent)
        .filter(
            ProviderEvent.provider == "sendgrid",
            ProviderEvent.org_id == "church-east",
        )
        .count()
        == 0
    )


def test_sendgrid_webhook_returns_retryable_error_when_processing_fails(
    client, monkeypatch
) -> None:
    monkeypatch.setattr(settings, "EMAIL_ENABLED", True)
    monkeypatch.setattr(webhooks, "_verify_sendgrid_signature", lambda *_args: True)
    monkeypatch.setattr(
        webhooks,
        "_apply_sendgrid_event",
        lambda *_args: (_ for _ in ()).throw(RuntimeError("database unavailable")),
    )

    response = _post(client, [{"event": "delivered"}])

    assert response.status_code == 503
    assert response.json() == {"detail": "SendGrid event processing failed"}
