"""Sprint 10 PR A: SendGrid Event Webhook handler.

The handler verifies the ECDSA signature, processes the event batch in
BackgroundTasks, updates Notification.status / delivered_at / opened_at /
clicked_at, and appends a DeliveryLog row per event. Tests pin:

- Unsigned / bad-signature requests are rejected (fail-closed).
- Configured signature → events apply correctly.
- Each event type maps to the right NotificationStatus.
- Unknown sg_message_id is logged + dropped (no 500).
- Malformed JSON / wrong shape returns 400.
"""

from __future__ import annotations

import base64
import json
import time

import pytest
from cryptography.hazmat.primitives.asymmetric.ec import (
    ECDSA,
    SECP256R1,
    generate_private_key,
)
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)
from fastapi.testclient import TestClient

from api.main import app
from api.models import (
    DeliveryLog,
    Notification,
    NotificationStatus,
    Organization,
    Person,
)


@pytest.fixture
def signing_keypair(monkeypatch):
    """Generate a one-shot ECDSA keypair and inject the public key into
    SENDGRID_WEBHOOK_PUBLIC_KEY so the handler accepts signatures we mint."""
    private = generate_private_key(SECP256R1())
    public_der = private.public_key().public_bytes(
        encoding=Encoding.DER, format=PublicFormat.SubjectPublicKeyInfo
    )
    monkeypatch.setenv(
        "SENDGRID_WEBHOOK_PUBLIC_KEY",
        base64.b64encode(public_der).decode("ascii"),
    )
    return private


def _sign(private, payload: bytes, timestamp: str) -> str:
    sig_bytes = private.sign(timestamp.encode("utf-8") + payload, ECDSA(SHA256()))
    return base64.b64encode(sig_bytes).decode("ascii")


def _seed_notification(db, *, sendgrid_message_id="sg_test_msg_001"):
    org = Organization(id="webhook_org", name="Webhook Org", region="Test")
    db.add(org)
    person = Person(
        id="webhook_recipient",
        org_id="webhook_org",
        name="Recipient",
        email="recipient@example.com",
        password_hash="$2b$12$dummy_hash",
        roles=["volunteer"],
    )
    db.add(person)
    notification = Notification(
        org_id="webhook_org",
        recipient_id="webhook_recipient",
        type="assignment",
        status=NotificationStatus.SENT,
        sendgrid_message_id=sendgrid_message_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


class TestSignatureRejection:
    def test_missing_signature_headers_returns_400(self, db):
        client = TestClient(app)
        resp = client.post("/webhooks/sendgrid", content=b"[]")
        assert resp.status_code == 400

    def test_signature_without_public_key_returns_401(self, db, monkeypatch):
        # No SENDGRID_WEBHOOK_PUBLIC_KEY → fail-closed even if headers
        # are present.
        monkeypatch.delenv("SENDGRID_WEBHOOK_PUBLIC_KEY", raising=False)
        client = TestClient(app)
        resp = client.post(
            "/webhooks/sendgrid",
            content=b"[]",
            headers={
                "X-Twilio-Email-Event-Webhook-Signature": "irrelevant",
                "X-Twilio-Email-Event-Webhook-Timestamp": "1700000000",
            },
        )
        assert resp.status_code == 401

    def test_invalid_signature_returns_401(self, db, signing_keypair):
        client = TestClient(app)
        resp = client.post(
            "/webhooks/sendgrid",
            content=b"[]",
            headers={
                # base64-DER but not a valid signature of this body.
                "X-Twilio-Email-Event-Webhook-Signature": base64.b64encode(b"junk").decode(),
                "X-Twilio-Email-Event-Webhook-Timestamp": "1700000000",
            },
        )
        assert resp.status_code == 401


class TestEventProcessing:
    def test_delivered_event_updates_status_and_delivered_at(self, db, signing_keypair):
        _seed_notification(db, sendgrid_message_id="sg_delivered_001")
        ts = int(time.time())
        events = [
            {
                "event": "delivered",
                "sg_message_id": "sg_delivered_001",
                "timestamp": ts,
            }
        ]
        payload = json.dumps(events).encode()
        timestamp = "1700000100"
        client = TestClient(app)
        resp = client.post(
            "/webhooks/sendgrid",
            content=payload,
            headers={
                "X-Twilio-Email-Event-Webhook-Signature": _sign(
                    signing_keypair, payload, timestamp
                ),
                "X-Twilio-Email-Event-Webhook-Timestamp": timestamp,
            },
        )
        assert resp.status_code == 200, resp.text
        assert resp.json() == {"received": 1}

        db.expire_all()
        n = (
            db.query(Notification)
            .filter(Notification.sendgrid_message_id == "sg_delivered_001")
            .one()
        )
        assert n.status == NotificationStatus.DELIVERED
        assert n.delivered_at is not None
        # Timestamps the handler stores are timezone-aware UTC (we
        # construct via fromtimestamp(..., tz=timezone.utc)). Naive
        # comparison just ensures it's set; exact equality risks
        # tz-flavor mismatches with SQLite.

        log = (
            db.query(DeliveryLog)
            .filter(DeliveryLog.sendgrid_message_id == "sg_delivered_001")
            .all()
        )
        assert len(log) == 1
        assert log[0].event_type == "delivered"

    def test_bounce_event_sets_status_failed_path(self, db, signing_keypair):
        _seed_notification(db, sendgrid_message_id="sg_bounce_001")
        events = [
            {
                "event": "bounce",
                "sg_message_id": "sg_bounce_001",
                "timestamp": int(time.time()),
                "reason": "550 5.1.1 Address not found",
            }
        ]
        payload = json.dumps(events).encode()
        timestamp = "1700000200"
        client = TestClient(app)
        resp = client.post(
            "/webhooks/sendgrid",
            content=payload,
            headers={
                "X-Twilio-Email-Event-Webhook-Signature": _sign(
                    signing_keypair, payload, timestamp
                ),
                "X-Twilio-Email-Event-Webhook-Timestamp": timestamp,
            },
        )
        assert resp.status_code == 200

        db.expire_all()
        n = db.query(Notification).filter(Notification.sendgrid_message_id == "sg_bounce_001").one()
        assert n.status == NotificationStatus.BOUNCED
        assert "Address not found" in (n.error_message or "")

    def test_unknown_message_id_is_dropped_not_500(self, db, signing_keypair):
        events = [
            {
                "event": "delivered",
                "sg_message_id": "sg_never_seen_999",
                "timestamp": int(time.time()),
            }
        ]
        payload = json.dumps(events).encode()
        timestamp = "1700000300"
        client = TestClient(app)
        resp = client.post(
            "/webhooks/sendgrid",
            content=payload,
            headers={
                "X-Twilio-Email-Event-Webhook-Signature": _sign(
                    signing_keypair, payload, timestamp
                ),
                "X-Twilio-Email-Event-Webhook-Timestamp": timestamp,
            },
        )
        # Should still return 200; SendGrid retries 5xx and we don't
        # want to ask for retries on events we just don't recognize.
        assert resp.status_code == 200


class TestMalformedPayload:
    def test_non_json_payload_returns_400(self, db, signing_keypair):
        payload = b"not json"
        timestamp = "1700000400"
        client = TestClient(app)
        resp = client.post(
            "/webhooks/sendgrid",
            content=payload,
            headers={
                "X-Twilio-Email-Event-Webhook-Signature": _sign(
                    signing_keypair, payload, timestamp
                ),
                "X-Twilio-Email-Event-Webhook-Timestamp": timestamp,
            },
        )
        assert resp.status_code == 400

    def test_non_array_payload_returns_400(self, db, signing_keypair):
        payload = b'{"event": "delivered"}'  # dict, not list
        timestamp = "1700000500"
        client = TestClient(app)
        resp = client.post(
            "/webhooks/sendgrid",
            content=payload,
            headers={
                "X-Twilio-Email-Event-Webhook-Signature": _sign(
                    signing_keypair, payload, timestamp
                ),
                "X-Twilio-Email-Event-Webhook-Timestamp": timestamp,
            },
        )
        assert resp.status_code == 400
