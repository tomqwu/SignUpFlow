"""Sprint 11.2 + 11.3 — forgot-password + reset-password web flow."""

from __future__ import annotations

from api.models import Person
from api.security import verify_password
from tests.web.conftest import seed_person


def test_forgot_page_renders(client):
    resp = client.get("/auth/forgot")
    assert resp.status_code == 200
    assert 'name="email"' in resp.text
    assert "Reset your password" in resp.text


def test_forgot_unknown_email_still_shows_sent(client, db):
    # No user enumeration: unknown email returns the same generic message.
    resp = client.post("/auth/forgot", data={"email": "nobody@example.com"})
    assert resp.status_code == 200
    assert "reset link is on its way" in resp.text.lower()


def test_forgot_invalid_email_shows_validation_error(client, db):
    resp = client.post("/auth/forgot", data={"email": "not-an-email"})
    assert resp.status_code == 400
    assert "valid email" in resp.text.lower()


def test_reset_page_renders_with_token(client):
    resp = client.get("/auth/reset/sometoken123")
    assert resp.status_code == 200
    assert 'action="/auth/reset/sometoken123"' in resp.text
    assert 'name="password"' in resp.text


def test_reset_invalid_token_shows_error(client, db):
    seed_person(db, email="reset-bad@example.com")
    resp = client.post(
        "/auth/reset/totally-invalid-token",
        data={"password": "BrandNewPass123!"},
    )
    assert resp.status_code in (400, 404)
    assert "error" in resp.text.lower() or "invalid" in resp.text.lower()


def test_reset_short_password_rejected(client, db):
    resp = client.post("/auth/reset/whatever", data={"password": "short"})
    assert resp.status_code == 400
    assert "at least 6" in resp.text.lower()


def test_full_reset_flow_changes_password(client, db, monkeypatch):
    """Real token: API forgot (debug-token on) → web reset → password
    actually changes and login works with the new one."""
    monkeypatch.setenv("DEBUG_RETURN_RESET_TOKEN", "true")
    seed_person(
        db,
        person_id="reset_user",
        email="resetme@example.com",
        password="OldPass123!",
    )
    issued = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "resetme@example.com"},
    )
    assert issued.status_code == 200
    token = issued.json()["token"]

    resp = client.post(f"/auth/reset/{token}", data={"password": "FreshPass456!"})
    assert resp.status_code == 303
    assert resp.headers["location"] == "/auth/login?reset=1"

    person = db.query(Person).filter(Person.id == "reset_user").first()
    db.refresh(person)
    assert verify_password("FreshPass456!", person.password_hash)
    assert not verify_password("OldPass123!", person.password_hash)


def test_login_shows_reset_banner(client):
    resp = client.get("/auth/login?reset=1")
    assert resp.status_code == 200
    assert "password updated" in resp.text.lower()
