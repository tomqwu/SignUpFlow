"""Provider-isolated safety tests for deferred SMS delivery policy."""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from api.models import Organization, Person, SmsPreference
from api.services.sms_service import SMSService
from api.timeutils import utcnow


@pytest.fixture
def enabled_sms(monkeypatch):
    client = MagicMock()
    monkeypatch.setenv("SMS_ENABLED", "true")
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "test-account")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "test-token")
    monkeypatch.setenv("TWILIO_PHONE_NUMBER", "+14165550000")
    monkeypatch.setattr("api.services.sms_service.Client", MagicMock(return_value=client))
    return SMSService(), client


def _recipient(db, *, verified: bool = True, opted_out: bool = False) -> None:
    db.add(Organization(id="sms-policy", name="SMS Policy"))
    db.add(
        Person(
            id="sms-recipient",
            org_id="sms-policy",
            name="Recipient",
            email="recipient@example.test",
            roles=["volunteer"],
        )
    )
    db.flush()
    db.add(
        SmsPreference(
            person_id="sms-recipient",
            phone_number="+14165550123",
            verified=verified,
            timezone="America/Toronto",
            opt_out_date=utcnow() - timedelta(days=1) if opted_out else None,
        )
    )
    db.commit()


@pytest.mark.parametrize(
    "verified,opted_out,expected",
    [
        (False, False, "Phone number not verified"),
        (True, True, "Recipient has opted out"),
    ],
)
def test_consent_denials_never_call_provider(db, enabled_sms, verified, opted_out, expected):
    service, client = enabled_sms
    _recipient(db, verified=verified, opted_out=opted_out)

    with pytest.raises(ValueError, match=expected):
        service.send_sms(
            db,
            recipient_id="sms-recipient",
            message_text="Schedule reminder",
            message_type="reminder",
            organization_id="sms-policy",
        )

    client.messages.create.assert_not_called()


def test_quiet_hours_denial_never_calls_provider(db, enabled_sms, monkeypatch):
    service, client = enabled_sms
    _recipient(db)
    monkeypatch.setattr(
        service.quiet_hours,
        "is_quiet_hours",
        MagicMock(return_value=(True, "local quiet hours")),
    )
    service.rate_limiter = SimpleNamespace(check_rate_limit=lambda *_: (True, 2))

    with pytest.raises(ValueError, match="local quiet hours"):
        service.send_sms(
            db,
            recipient_id="sms-recipient",
            message_text="Schedule reminder",
            message_type="reminder",
            organization_id="sms-policy",
        )

    client.messages.create.assert_not_called()
