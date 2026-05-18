"""Marathon P2.15 — email-delivery status on the settings page."""

from __future__ import annotations

from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_email_section_disabled_by_default(client, db):
    tok = _admin(client, db, org="em_o1", email="em1@web.test")
    resp = client.get("/a/settings", cookies={SESSION_COOKIE: tok})
    assert resp.status_code == 200
    assert "Email delivery" in resp.text
    # TESTING=true globally → email gate off → guidance shown.
    assert "EMAIL_ENABLED" in resp.text
    assert "disabled" in resp.text


def test_email_section_enabled_with_smtp(client, db, monkeypatch):
    tok = _admin(client, db, org="em_o2", email="em2@web.test")
    monkeypatch.setenv("TESTING", "")
    monkeypatch.setenv("EMAIL_ENABLED", "true")
    monkeypatch.setenv("MAILTRAP_SMTP_USER", "sandbox-user")
    monkeypatch.setenv("MAILTRAP_SMTP_PASSWORD", "sandbox-pass")
    resp = client.get("/a/settings", cookies={SESSION_COOKIE: tok})
    assert resp.status_code == 200
    assert "SMTP / Mailtrap" in resp.text
    assert "Sending as" in resp.text
