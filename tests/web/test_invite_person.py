"""Sprint 11.14 — admin invite person."""

from __future__ import annotations

from unittest.mock import MagicMock

from api.models import Invitation, Person
from api.routers import invitations
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org="i_org", email="iadmin@web.test"):
    seed_person(db, person_id="i_admin", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_people_page_has_invite_form(client, db):
    token = _admin(client, db)
    resp = client.get("/a/people", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Invite person" in resp.text
    assert 'hx-post="/a/people/invite"' in resp.text


def test_invite_creates_invitation(client, db):
    token = _admin(client, db, org="i_org2", email="iadmin2@web.test")
    resp = client.post(
        "/a/people/invite",
        data={
            "name": "Jamie Park",
            "email": "jamie@example.com",
            "role": "volunteer",
        },
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert "Invitation created for jamie@example.com" in resp.text
    assert "Email delivery is disabled" in resp.text
    assert resp.headers["cache-control"] == "no-store"
    inv = db.query(Invitation).filter(Invitation.email == "jamie@example.com").first()
    assert inv is not None
    assert inv.org_id == "i_org2"
    assert inv.roles == ["volunteer"]
    assert inv.status == "pending"
    assert f'data-invite-link="/auth/invitation/{inv.token}"' in resp.text
    assert 'id="invite-link"' in resp.text
    assert "Copy link" in resp.text


def test_invite_admin_role(client, db):
    token = _admin(client, db, org="i_org3", email="iadmin3@web.test")
    client.post(
        "/a/people/invite",
        data={
            "name": "New Admin",
            "email": "newadmin@example.com",
            "role": "admin",
        },
        cookies={SESSION_COOKIE: token},
    )
    inv = db.query(Invitation).filter(Invitation.email == "newadmin@example.com").first()
    assert inv.roles == ["admin"]


def test_manual_invite_uses_configured_public_url(client, db, monkeypatch):
    token = _admin(client, db, org="i_public", email="public-admin@web.test")
    monkeypatch.setenv("FRONTEND_URL", "https://signup.example/")

    response = client.post(
        "/a/people/invite",
        data={"name": "Public Member", "email": "public@example.com", "role": "volunteer"},
        cookies={SESSION_COOKIE: token},
    )

    assert response.status_code == 200
    invitation = (
        db.query(Invitation)
        .filter(Invitation.org_id == "i_public", Invitation.email == "public@example.com")
        .one()
    )
    assert (
        f'data-invite-link="https://signup.example/auth/invitation/{invitation.token}"'
        in response.text
    )


def test_manual_invite_rejects_private_origin_when_public_url_configured(client, db, monkeypatch):
    token = _admin(client, db, org="i_origin", email="origin-admin@web.test")
    monkeypatch.setenv("FRONTEND_URL", "https://signup.example/")

    response = client.post(
        "/a/people/invite",
        data={"name": "Private Member", "email": "private@example.com", "role": "volunteer"},
        headers={"Origin": "http://private.example"},
        cookies={SESSION_COOKIE: token},
    )

    assert response.status_code == 403
    assert (
        db.query(Invitation)
        .filter(Invitation.org_id == "i_origin", Invitation.email == "private@example.com")
        .first()
        is None
    )


def test_invite_volunteer_with_scheduling_qualifications(client, db):
    token = _admin(client, db, org="i_org_roles", email="roles-admin@web.test")
    response = client.post(
        "/a/people/invite",
        data={
            "name": "Qualified Member",
            "email": "qualified@example.com",
            "role": "volunteer",
            "qualifications": "worship_leader, sound",
        },
        cookies={SESSION_COOKIE: token},
    )

    assert response.status_code == 200
    invitation = (
        db.query(Invitation)
        .filter(
            Invitation.org_id == "i_org_roles",
            Invitation.email == "qualified@example.com",
        )
        .one()
    )
    assert invitation.roles == ["volunteer", "worship_leader", "sound"]

    client.cookies.clear()
    accepted = client.post(
        f"/auth/invitation/{invitation.token}",
        data={"password": "QualifiedPass123!"},
    )
    assert accepted.status_code == 303
    assert accepted.headers["location"] == "/v/schedule"
    member = (
        db.query(Person)
        .filter(Person.org_id == "i_org_roles", Person.email == "qualified@example.com")
        .one()
    )
    assert member.roles == ["volunteer", "worship_leader", "sound"]
    admin_page = client.get("/a/people")
    assert admin_page.status_code == 303
    assert admin_page.headers["location"] == "/auth/login"


def test_invite_rejects_permission_names_as_qualifications(client, db):
    token = _admin(client, db, org="i_org_reserved", email="reserved-admin@web.test")

    response = client.post(
        "/a/people/invite",
        data={
            "name": "Not Admin",
            "email": "not-admin@example.com",
            "role": "volunteer",
            "qualifications": "usher, Admin",
        },
        cookies={SESSION_COOKIE: token},
    )

    assert response.status_code == 400
    assert "reserved" in response.text.lower()
    assert (
        db.query(Invitation)
        .filter(
            Invitation.org_id == "i_org_reserved",
            Invitation.email == "not-admin@example.com",
        )
        .first()
        is None
    )


def test_invite_invalid_email_rejected(client, db):
    token = _admin(client, db, org="i_org4", email="iadmin4@web.test")
    resp = client.post(
        "/a/people/invite",
        data={"name": "Bad", "email": "not-an-email", "role": "volunteer"},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 400
    assert "form-error" in resp.text
    # Scope by org — the strict tenancy guard rejects bare cross-tenant
    # SELECTs (including from test code).
    assert (
        db.query(Invitation).filter(Invitation.org_id == "i_org4", Invitation.name == "Bad").first()
        is None
    )


def test_invite_requires_admin(client, db):
    seed_person(db, person_id="i_vol", email="ivol@web.test", roles=["volunteer"])
    login = client.post(
        "/auth/login",
        data={"email": "ivol@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    resp = client.post(
        "/a/people/invite",
        data={"name": "X", "email": "x@example.com", "role": "volunteer"},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "/auth/login"


def test_invite_requires_auth(client):
    resp = client.post(
        "/a/people/invite",
        data={"name": "X", "email": "x@example.com", "role": "volunteer"},
    )
    assert resp.status_code == 303


def test_browser_invite_executes_email_task(client, db, monkeypatch, tmp_path):
    token = _admin(client, db)
    monkeypatch.setenv("FRONTEND_URL", "https://signup.example/")
    monkeypatch.setattr(invitations.email_service, "capture_dir", tmp_path)
    send = MagicMock(return_value=True)
    monkeypatch.setattr(invitations.email_service, "send_email", send)
    response = client.post(
        "/a/people/invite",
        data={"name": "Jamie", "email": "delivery@example.com", "role": "volunteer"},
        cookies={SESSION_COOKIE: token},
    )
    assert response.status_code == 200
    assert 'id="invite-link"' not in response.text
    send.assert_called_once()
    invitation = (
        db.query(Invitation)
        .filter(Invitation.org_id == "i_org", Invitation.email == "delivery@example.com")
        .one()
    )
    path = f"/auth/invitation/{invitation.token}"
    _, _, html_body, plain_body = send.call_args.args
    assert f"https://signup.example{path}" in html_body
    assert f"https://signup.example{path}" in plain_body
    client.cookies.clear()
    assert client.get(path).status_code == 200
    accepted = client.post(path, data={"password": "InvitePass123!"})
    assert accepted.status_code == 303
    assert accepted.headers["location"] == "/v/schedule"
