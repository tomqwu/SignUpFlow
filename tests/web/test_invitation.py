"""Sprint 11.4 — invitation accept web flow."""

from __future__ import annotations

from datetime import timedelta

from api.models import Invitation, Person
from api.timeutils import utcnow
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _seed_invite(
    db,
    *,
    token="invite-tok-123",
    org_id="web_org",
    email="newvol@example.com",
    name="New Vol",
    roles=None,
    status="pending",
    expires_in=timedelta(days=3),
):
    admin = seed_person(
        db,
        person_id="inv_admin",
        org_id=org_id,
        email="invadmin@example.com",
        roles=["admin"],
    )
    inv = Invitation(
        id=f"inv_{token}",
        org_id=org_id,
        email=email,
        name=name,
        roles=roles if roles is not None else ["volunteer"],
        invited_by=admin.id,
        token=token,
        status=status,
        expires_at=utcnow() + expires_in,
    )
    db.add(inv)
    db.commit()
    return inv


def test_invitation_page_renders_for_valid_token(client, db):
    _seed_invite(db, name="Jamie Park", email="jamie@example.com")
    resp = client.get("/auth/invitation/invite-tok-123")
    assert resp.status_code == 200
    assert "Jamie Park" in resp.text
    assert "jamie@example.com" in resp.text
    assert 'name="password"' in resp.text


def test_invitation_invalid_token_shows_error(client, db):
    resp = client.get("/auth/invitation/does-not-exist")
    assert resp.status_code == 410
    assert "invalid" in resp.text.lower()


def test_invitation_expired_token_shows_error(client, db):
    _seed_invite(db, token="exp-tok", expires_in=timedelta(days=-1))
    resp = client.get("/auth/invitation/exp-tok")
    assert resp.status_code == 410
    assert "expired" in resp.text.lower()


def test_accept_invitation_creates_account_and_authenticates(client, db):
    _seed_invite(db, token="acc-tok", email="accepter@example.com", roles=["volunteer"])
    resp = client.post("/auth/invitation/acc-tok", data={"password": "MyNewPass123!"})
    assert resp.status_code == 303
    assert resp.headers["location"] == "/v/schedule"
    assert SESSION_COOKIE in resp.cookies

    # Account created with the invited email + role.
    person = db.query(Person).filter(Person.email == "accepter@example.com").first()
    assert person is not None
    assert person.roles == ["volunteer"]

    # Session works.
    token = resp.cookies[SESSION_COOKIE]
    sched = client.get("/v/schedule", cookies={SESSION_COOKIE: token})
    assert sched.status_code == 200


def test_accept_admin_invitation_lands_on_dashboard(client, db):
    _seed_invite(db, token="adm-tok", email="newadmin@example.com", roles=["admin"])
    resp = client.post("/auth/invitation/adm-tok", data={"password": "AdminPass123!"})
    assert resp.status_code == 303
    assert resp.headers["location"] == "/a/dashboard"


def test_accept_short_password_rejected(client, db):
    _seed_invite(db, token="short-tok")
    resp = client.post("/auth/invitation/short-tok", data={"password": "x"})
    assert resp.status_code == 400
    assert "at least 6" in resp.text.lower()
    assert SESSION_COOKIE not in resp.cookies


def test_accept_already_accepted_invitation_errors(client, db):
    _seed_invite(db, token="used-tok", status="accepted")
    resp = client.post("/auth/invitation/used-tok", data={"password": "WhateverPass1!"})
    assert resp.status_code in (400, 410)
    assert SESSION_COOKIE not in resp.cookies
