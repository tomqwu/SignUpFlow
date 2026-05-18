"""Marathon P2.16 — SMS-notifications status on the settings page."""

from __future__ import annotations

from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_sms_section_disabled_by_default(client, db):
    tok = _admin(client, db, org="sm_o1", email="sm1@web.test")
    resp = client.get("/a/settings", cookies={SESSION_COOKIE: tok})
    assert resp.status_code == 200
    assert "SMS notifications" in resp.text
    assert "disabled" in resp.text
    assert "+15005550006" in resp.text  # Twilio magic-number sandbox hint


def test_sms_section_active_with_creds(client, db, monkeypatch):
    tok = _admin(client, db, org="sm_o2", email="sm2@web.test")
    monkeypatch.setenv("SMS_ENABLED", "true")
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACxxx")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "tok")
    monkeypatch.setenv("TWILIO_PHONE_NUMBER", "+15005550006")
    resp = client.get("/a/settings", cookies={SESSION_COOKIE: tok})
    assert resp.status_code == 200
    assert "active" in resp.text
    assert "broadcasts can be sent" in resp.text


def test_sms_section_misconfigured(client, db, monkeypatch):
    tok = _admin(client, db, org="sm_o3", email="sm3@web.test")
    monkeypatch.setenv("SMS_ENABLED", "true")
    monkeypatch.delenv("TWILIO_ACCOUNT_SID", raising=False)
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWILIO_PHONE_NUMBER", raising=False)
    resp = client.get("/a/settings", cookies={SESSION_COOKIE: tok})
    assert resp.status_code == 200
    assert "misconfigured" in resp.text
