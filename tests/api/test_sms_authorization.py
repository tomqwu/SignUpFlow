"""Tenant and callback safety for the deferred SMS surface."""

from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from twilio.request_validator import RequestValidator

from api.core.config import settings
from api.models import (
    Assignment,
    Event,
    Organization,
    Person,
    SmsMessage,
    SmsPreference,
    SmsReply,
    SmsUsage,
)
from api.security import create_access_token
from api.services.sms_service import SMSService
from api.timeutils import utcnow

pytestmark = pytest.mark.no_mock_auth

AUTH_TOKEN = "test-twilio-auth-token"
INCOMING_URL = "http://testserver/api/sms/webhook/incoming-sms"
STATUS_URL = "http://testserver/api/sms/webhook/delivery-status"


@pytest.fixture(autouse=True)
def _enable_sms_sandbox(monkeypatch):
    monkeypatch.setattr(settings, "SMS_ENABLED", True)
    monkeypatch.setenv("SMS_ENABLED", "true")
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC00000000000000000000000000000000")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", AUTH_TOKEN)
    monkeypatch.setenv("TWILIO_PHONE_NUMBER", "+14165550100")
    monkeypatch.setenv("TWILIO_INCOMING_SMS_URL", INCOMING_URL)
    monkeypatch.setenv("TWILIO_STATUS_CALLBACK_URL", STATUS_URL)


@pytest.fixture
def sms_actors(db):
    db.add_all(
        [
            Organization(id="sms-org-a", name="SMS Org A"),
            Organization(id="sms-org-b", name="SMS Org B"),
        ]
    )
    db.flush()

    people = {}
    for person_id, org_id, roles in [
        ("sms-admin-a", "sms-org-a", ["admin"]),
        ("sms-volunteer-a", "sms-org-a", ["volunteer"]),
        ("sms-other-a", "sms-org-a", ["volunteer"]),
        ("sms-admin-b", "sms-org-b", ["admin"]),
        ("sms-volunteer-b", "sms-org-b", ["volunteer"]),
    ]:
        person = Person(
            id=person_id,
            org_id=org_id,
            name=person_id,
            email=f"{person_id}@example.com",
            roles=roles,
        )
        db.add(person)
        people[person_id] = person

    db.flush()
    db.add_all(
        [
            SmsPreference(
                person_id="sms-volunteer-a",
                phone_number="+14165550101",
                verified=True,
                notification_types=["assignment"],
            ),
            SmsPreference(
                person_id="sms-other-a",
                phone_number="+14165550102",
                verified=True,
                notification_types=["assignment"],
            ),
            SmsPreference(
                person_id="sms-volunteer-b",
                phone_number="+14165550103",
                verified=True,
                notification_types=["assignment"],
            ),
        ]
    )
    db.commit()

    return {
        person_id: {
            "Authorization": (
                "Bearer " + create_access_token({"sub": person.id, "org_id": person.org_id})
            )
        }
        for person_id, person in people.items()
    }


def _signed_headers(url: str, params: dict[str, str]) -> dict[str, str]:
    signature = RequestValidator(AUTH_TOKEN).compute_signature(url, params)
    return {"X-Twilio-Signature": signature}


def test_verification_accepts_own_string_id_and_denies_other_targets_before_service(
    client, sms_actors, monkeypatch
):
    service = MagicMock()
    service.generate_verification_code.return_value = 123456
    service_factory = MagicMock(return_value=service)
    monkeypatch.setattr("api.routers.sms.SMSService", service_factory)

    allowed = client.post(
        "/api/sms/send-verification-code",
        headers=sms_actors["sms-volunteer-a"],
        json={"person_id": "sms-volunteer-a", "phone_number": "+14165550101"},
    )
    assert allowed.status_code == 200, allowed.text
    assert service.generate_verification_code.call_args.kwargs["person_id"] == "sms-volunteer-a"

    service.reset_mock()
    service_factory.reset_mock()
    for headers, target in [
        (sms_actors["sms-volunteer-a"], "sms-other-a"),
        (sms_actors["sms-admin-b"], "sms-volunteer-a"),
    ]:
        denied = client.post(
            "/api/sms/send-verification-code",
            headers=headers,
            json={"person_id": target, "phone_number": "+14165550104"},
        )
        assert denied.status_code in {403, 404}, denied.text

    service_factory.assert_not_called()
    service.generate_verification_code.assert_not_called()


def test_preferences_use_exact_string_ids_and_preserve_unauthorized_state(client, db, sms_actors):
    allowed = client.put(
        "/api/sms/people/sms-volunteer-a/sms-preferences",
        headers=sms_actors["sms-volunteer-a"],
        json={"notification_types": ["assignment", "reminder"], "language": "fr"},
    )
    assert allowed.status_code == 200, allowed.text

    for headers, target in [
        (sms_actors["sms-volunteer-a"], "sms-other-a"),
        (sms_actors["sms-admin-b"], "sms-volunteer-a"),
    ]:
        denied = client.put(
            f"/api/sms/people/{target}/sms-preferences",
            headers=headers,
            json={"notification_types": ["cancellation"], "language": "zh-CN"},
        )
        assert denied.status_code in {403, 404}, denied.text

    db.expire_all()
    own = db.get(SmsPreference, "sms-volunteer-a")
    other = db.get(SmsPreference, "sms-other-a")
    assert own.notification_types == ["assignment", "reminder"]
    assert own.language == "fr"
    assert other.notification_types == ["assignment"]
    assert other.language == "en"


def test_usage_uses_exact_string_org_id_and_real_model_counters(client, db, sms_actors):
    db.add(
        SmsUsage(
            organization_id="sms-org-a",
            month_year=utcnow().strftime("%Y-%m"),
            assignment_count=2,
            reminder_count=3,
            broadcast_count=1,
            system_count=0,
            total_cost_cents=6,
            budget_limit_cents=10000,
        )
    )
    db.commit()

    response = client.get(
        "/api/sms/organizations/sms-org-a/sms-usage",
        headers=sms_actors["sms-admin-a"],
    )

    assert response.status_code == 200, response.text
    assert response.json()["messages_sent"] == 6
    foreign = client.get(
        "/api/sms/organizations/sms-org-a/sms-usage",
        headers=sms_actors["sms-admin-b"],
    )
    assert foreign.status_code == 403, foreign.text


def test_assignment_notification_requires_one_tenant_consistent_tuple(
    client, db, sms_actors, monkeypatch
):
    starts = utcnow() + timedelta(days=1)
    db.add_all(
        [
            Event(
                id="sms-event-a",
                org_id="sms-org-a",
                type="Practice",
                start_time=starts,
                end_time=starts + timedelta(hours=1),
            ),
            Event(
                id="sms-event-b",
                org_id="sms-org-b",
                type="Practice",
                start_time=starts,
                end_time=starts + timedelta(hours=1),
            ),
        ]
    )
    db.flush()
    assignment = Assignment(event_id="sms-event-a", person_id="sms-volunteer-a", role="scorekeeper")
    db.add(assignment)
    db.commit()

    queued = MagicMock()
    queued.return_value.id = "task-1"
    monkeypatch.setattr("api.routers.sms.send_assignment_notification.delay", queued)

    for payload in [
        {
            "assignment_id": assignment.id,
            "event_id": "sms-event-b",
            "person_id": "sms-volunteer-a",
        },
        {
            "assignment_id": assignment.id,
            "event_id": "sms-event-a",
            "person_id": "sms-other-a",
        },
    ]:
        response = client.post(
            "/api/sms/send-assignment-notification",
            headers=sms_actors["sms-admin-a"],
            json=payload,
        )
        assert response.status_code == 404, response.text

    queued.assert_not_called()

    valid = client.post(
        "/api/sms/send-assignment-notification",
        headers=sms_actors["sms-admin-a"],
        json={
            "assignment_id": assignment.id,
            "event_id": "sms-event-a",
            "person_id": "sms-volunteer-a",
        },
    )
    assert valid.status_code == 200, valid.text
    queued.assert_called_once_with(
        assignment_id=assignment.id,
        event_id="sms-event-a",
        person_id="sms-volunteer-a",
        organization_id="sms-org-a",
        language="en",
    )


def test_foreign_event_reminder_is_denied_before_queue(client, db, sms_actors, monkeypatch):
    starts = utcnow() + timedelta(days=1)
    db.add(
        Event(
            id="sms-foreign-event",
            org_id="sms-org-b",
            type="Game",
            start_time=starts,
            end_time=starts + timedelta(hours=2),
        )
    )
    db.commit()
    queued = MagicMock()
    monkeypatch.setattr("api.routers.sms.send_event_reminder.delay", queued)

    response = client.post(
        "/api/sms/send-event-reminder",
        headers=sms_actors["sms-admin-a"],
        json={"event_id": "sms-foreign-event"},
    )

    assert response.status_code == 404, response.text
    queued.assert_not_called()


@pytest.mark.parametrize(
    "recipient_ids",
    [
        ["sms-volunteer-a", "sms-volunteer-b"],
        ["sms-volunteer-a"] * 201,
        ["sms-volunteer-a", "sms-volunteer-a"],
    ],
)
def test_broadcast_rejects_invalid_recipient_sets_atomically(
    client, sms_actors, monkeypatch, recipient_ids
):
    queued = MagicMock()
    monkeypatch.setattr("api.routers.sms.send_broadcast_message.delay", queued)

    response = client.post(
        "/api/sms/send-broadcast",
        headers=sms_actors["sms-admin-a"],
        json={"recipient_ids": recipient_ids, "message_text": "Practice moved to 7 PM"},
    )

    assert response.status_code in {404, 422}, response.text
    queued.assert_not_called()


def test_broadcast_queues_only_same_tenant_string_ids(client, sms_actors, monkeypatch):
    queued = MagicMock()
    queued.return_value.id = "task-2"
    monkeypatch.setattr("api.routers.sms.send_broadcast_message.delay", queued)

    response = client.post(
        "/api/sms/send-broadcast",
        headers=sms_actors["sms-admin-a"],
        json={
            "recipient_ids": ["sms-volunteer-a", "sms-other-a"],
            "message_text": "Practice moved to 7 PM",
        },
    )

    assert response.status_code == 200, response.text
    queued.assert_called_once_with(
        recipient_ids=["sms-volunteer-a", "sms-other-a"],
        message_text="Practice moved to 7 PM",
        organization_id="sms-org-a",
        is_urgent=False,
    )


def test_broadcast_service_rejects_mixed_tenants_before_send(db, sms_actors):
    service = SMSService.__new__(SMSService)
    service.send_sms = MagicMock()
    service.cost_tracker = MagicMock()

    with pytest.raises(ValueError, match="recipients were not found"):
        service.send_broadcast(
            db=db,
            recipient_ids=["sms-volunteer-a", "sms-volunteer-b"],
            message_text="Practice moved to 7 PM",
            organization_id="sms-org-a",
        )

    service.send_sms.assert_not_called()
    service.cost_tracker.calculate_cost.assert_not_called()


def test_assignment_worker_rechecks_tuple_before_service(db, sms_actors, monkeypatch):
    from api.tasks import sms_tasks

    starts = utcnow() + timedelta(days=1)
    event = Event(
        id="sms-worker-event",
        org_id="sms-org-a",
        type="Practice",
        start_time=starts,
        end_time=starts + timedelta(hours=1),
    )
    db.add(event)
    db.flush()
    assignment = Assignment(
        event_id=event.id,
        person_id="sms-volunteer-a",
        role="scorekeeper",
    )
    db.add(assignment)
    db.commit()

    service_factory = MagicMock()
    monkeypatch.setattr(sms_tasks, "SessionLocal", lambda: db)
    monkeypatch.setattr(sms_tasks, "SMSService", service_factory)

    def reject_retry(*, exc, countdown):
        raise RuntimeError(str(exc))

    monkeypatch.setattr(sms_tasks.send_assignment_notification, "retry", reject_retry)

    with pytest.raises(RuntimeError, match=f"Assignment {assignment.id} not found"):
        sms_tasks.send_assignment_notification.run(
            assignment.id,
            event.id,
            "sms-other-a",
            "sms-org-a",
        )

    service_factory.assert_not_called()


def test_disabled_callbacks_cannot_mutate_preferences(client, db, sms_actors, monkeypatch):
    monkeypatch.setattr(settings, "SMS_ENABLED", False)
    params = {
        "From": "+14165550101",
        "Body": "STOP",
        "MessageSid": "SM-disabled-callback",
    }

    response = client.post("/api/sms/webhook/incoming-sms", data=params)

    assert response.status_code == 404, response.text
    db.expire_all()
    assert db.get(SmsPreference, "sms-volunteer-a").opt_out_date is None
    assert db.query(SmsReply).count() == 0


@pytest.mark.parametrize("signature", [None, "invalid-signature"])
def test_incoming_callback_rejects_missing_or_invalid_signature_without_mutation(
    client, db, sms_actors, signature
):
    params = {
        "From": "+14165550101",
        "Body": "STOP",
        "MessageSid": "SM-incoming-invalid",
    }
    headers = {"X-Twilio-Signature": signature} if signature else {}

    response = client.post("/api/sms/webhook/incoming-sms", data=params, headers=headers)

    assert response.status_code == 403, response.text
    db.expire_all()
    assert db.get(SmsPreference, "sms-volunteer-a").opt_out_date is None
    assert db.query(SmsReply).count() == 0


def test_signed_incoming_callback_is_processed_once(client, db, sms_actors):
    params = {
        "From": "+14165550101",
        "Body": "STOP",
        "MessageSid": "SM-incoming-valid",
    }
    headers = _signed_headers(INCOMING_URL, params)

    first = client.post("/api/sms/webhook/incoming-sms", data=params, headers=headers)
    assert first.status_code == 200, first.text
    assert first.json()["action_taken"] == "opted_out"

    db.expire_all()
    first_opt_out = db.get(SmsPreference, "sms-volunteer-a").opt_out_date
    assert first_opt_out is not None
    assert db.query(SmsReply).filter_by(twilio_message_sid="SM-incoming-valid").count() == 1

    second = client.post("/api/sms/webhook/incoming-sms", data=params, headers=headers)
    assert second.status_code == 200, second.text
    assert second.json()["status"] == "duplicate"

    db.expire_all()
    assert db.get(SmsPreference, "sms-volunteer-a").opt_out_date == first_opt_out
    assert db.query(SmsReply).filter_by(twilio_message_sid="SM-incoming-valid").count() == 1


def test_signed_delivery_callback_updates_known_message_once(client, db, sms_actors):
    message = SmsMessage(
        organization_id="sms-org-a",
        recipient_id="sms-volunteer-a",
        phone_number="+14165550101",
        message_text="Practice reminder",
        message_type="reminder",
        status="sent",
        twilio_message_sid="SM-outgoing-valid",
    )
    db.add(message)
    db.commit()
    params = {
        "MessageSid": "SM-outgoing-valid",
        "MessageStatus": "delivered",
    }
    headers = _signed_headers(STATUS_URL, params)

    first = client.post("/api/sms/webhook/delivery-status", data=params, headers=headers)
    assert first.status_code == 200, first.text
    db.expire_all()
    delivered_at = db.get(SmsMessage, message.id).delivered_at
    assert delivered_at is not None

    second = client.post("/api/sms/webhook/delivery-status", data=params, headers=headers)
    assert second.status_code == 200, second.text
    assert second.json()["status"] == "duplicate"
    db.expire_all()
    stored = db.get(SmsMessage, message.id)
    assert stored.status == "delivered"
    assert stored.delivered_at == delivered_at


@pytest.mark.parametrize("signature", [None, "invalid-signature"])
def test_delivery_callback_rejects_bad_signature_without_mutation(
    client, db, sms_actors, signature
):
    message = SmsMessage(
        organization_id="sms-org-a",
        recipient_id="sms-volunteer-a",
        phone_number="+14165550101",
        message_text="Practice reminder",
        message_type="reminder",
        status="sent",
        twilio_message_sid="SM-delivery-invalid",
    )
    db.add(message)
    db.commit()
    params = {"MessageSid": "SM-delivery-invalid", "MessageStatus": "delivered"}
    headers = {"X-Twilio-Signature": signature} if signature else {}

    response = client.post("/api/sms/webhook/delivery-status", data=params, headers=headers)

    assert response.status_code == 403, response.text
    db.expire_all()
    stored = db.get(SmsMessage, message.id)
    assert stored.status == "sent"
    assert stored.delivered_at is None


def test_delivery_callback_rejects_unknown_status_without_mutation(client, db, sms_actors):
    message = SmsMessage(
        organization_id="sms-org-a",
        recipient_id="sms-volunteer-a",
        phone_number="+14165550101",
        message_text="Practice reminder",
        message_type="reminder",
        status="sent",
        twilio_message_sid="SM-status-invalid",
    )
    db.add(message)
    db.commit()
    params = {"MessageSid": "SM-status-invalid", "MessageStatus": "invented"}

    response = client.post(
        "/api/sms/webhook/delivery-status",
        data=params,
        headers=_signed_headers(STATUS_URL, params),
    )

    assert response.status_code == 422, response.text
    db.expire_all()
    assert db.get(SmsMessage, message.id).status == "sent"


def test_delivery_callback_cannot_regress_a_successful_terminal_status(client, db, sms_actors):
    message = SmsMessage(
        organization_id="sms-org-a",
        recipient_id="sms-volunteer-a",
        phone_number="+14165550101",
        message_text="Practice reminder",
        message_type="reminder",
        status="delivered",
        twilio_message_sid="SM-status-regression",
        delivered_at=utcnow(),
    )
    db.add(message)
    db.commit()
    delivered_at = message.delivered_at
    params = {
        "MessageSid": "SM-status-regression",
        "MessageStatus": "failed",
        "ErrorMessage": "Late provider callback",
    }

    response = client.post(
        "/api/sms/webhook/delivery-status",
        data=params,
        headers=_signed_headers(STATUS_URL, params),
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "duplicate"
    db.expire_all()
    stored = db.get(SmsMessage, message.id)
    assert stored.status == "delivered"
    assert stored.delivered_at == delivered_at
    assert stored.failed_at is None
    assert stored.error_message is None
