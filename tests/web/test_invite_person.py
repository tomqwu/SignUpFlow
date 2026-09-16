"""Sprint 11.14 — admin invite person."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock

from api.models import Invitation, Person
from api.routers import invitations
from api.timeutils import utcnow
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org="i_org", email="iadmin@web.test", person_id="i_admin"):
    seed_person(db, person_id=person_id, org_id=org, email=email, roles=["admin"])
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


def test_pending_invitation_link_survives_people_refresh(client, db):
    token = _admin(client, db, org="i_pending", email="pending-admin@web.test")
    client.post(
        "/a/people/invite",
        data={"name": "Pending Member", "email": "pending@example.com", "role": "volunteer"},
        cookies={SESSION_COOKIE: token},
    )
    invitation = (
        db.query(Invitation)
        .filter(Invitation.org_id == "i_pending", Invitation.email == "pending@example.com")
        .one()
    )

    page = client.get("/a/people", cookies={SESSION_COOKIE: token})

    assert page.status_code == 200
    assert page.headers["cache-control"] == "no-store"
    assert "Pending Member" in page.text
    assert f'data-invite-link="/auth/invitation/{invitation.token}"' in page.text
    assert f'action="/a/people/invitations/{invitation.id}/cancel"' in page.text


def test_people_page_hides_other_org_invitations(client, db):
    first_token = _admin(client, db, org="i_first", email="first-admin@web.test")
    client.post(
        "/a/people/invite",
        data={"name": "Other Member", "email": "other@example.com", "role": "volunteer"},
        cookies={SESSION_COOKIE: first_token},
    )
    other_invitation = (
        db.query(Invitation)
        .filter(Invitation.org_id == "i_first", Invitation.email == "other@example.com")
        .one()
    )
    second_token = _admin(
        client, db, org="i_second", email="second-admin@web.test", person_id="i_second_admin"
    )

    page = client.get("/a/people", cookies={SESSION_COOKIE: second_token})

    assert "other@example.com" not in page.text
    assert other_invitation.token not in page.text


def test_cancel_pending_invitation_allows_recreation(client, db):
    token = _admin(client, db, org="i_cancel", email="cancel-admin@web.test")
    invite_data = {"name": "Cancel Member", "email": "cancel@example.com", "role": "volunteer"}
    client.post("/a/people/invite", data=invite_data, cookies={SESSION_COOKIE: token})
    invitation = (
        db.query(Invitation)
        .filter(Invitation.org_id == "i_cancel", Invitation.email == "cancel@example.com")
        .one()
    )

    cancelled = client.post(
        f"/a/people/invitations/{invitation.id}/cancel", cookies={SESSION_COOKIE: token}
    )

    assert cancelled.status_code == 303
    assert cancelled.headers["location"] == "/a/people"
    db.refresh(invitation)
    assert invitation.status == "cancelled"
    assert invitation.token not in client.get("/a/people", cookies={SESSION_COOKIE: token}).text
    recreated = client.post("/a/people/invite", data=invite_data, cookies={SESSION_COOKIE: token})
    assert recreated.status_code == 200
    assert "Invitation created" in recreated.text


def test_cancel_other_org_invitation_is_not_found(client, db):
    first_token = _admin(client, db, org="i_owner", email="owner-admin@web.test")
    client.post(
        "/a/people/invite",
        data={"name": "Owner Member", "email": "owner@example.com", "role": "volunteer"},
        cookies={SESSION_COOKIE: first_token},
    )
    invitation = (
        db.query(Invitation)
        .filter(Invitation.org_id == "i_owner", Invitation.email == "owner@example.com")
        .one()
    )
    second_token = _admin(
        client, db, org="i_attacker", email="attacker-admin@web.test", person_id="i_attacker_admin"
    )

    response = client.post(
        f"/a/people/invitations/{invitation.id}/cancel", cookies={SESSION_COOKIE: second_token}
    )

    assert response.status_code == 404
    db.refresh(invitation)
    assert invitation.status == "pending"


def test_cancel_invitation_requires_admin(client, db):
    token = _admin(client, db, org="i_guard", email="guard-admin@web.test")
    client.post(
        "/a/people/invite",
        data={"name": "Guard Member", "email": "guard@example.com", "role": "volunteer"},
        cookies={SESSION_COOKIE: token},
    )
    invitation = (
        db.query(Invitation)
        .filter(Invitation.org_id == "i_guard", Invitation.email == "guard@example.com")
        .one()
    )
    client.cookies.clear()

    response = client.post(f"/a/people/invitations/{invitation.id}/cancel")

    assert response.status_code == 303
    assert response.headers["location"] == "/auth/login"
    db.refresh(invitation)
    assert invitation.status == "pending"


def test_expired_pending_invitation_cannot_be_copied(client, db):
    token = _admin(client, db, org="i_expired", email="expired-admin@web.test")
    client.post(
        "/a/people/invite",
        data={"name": "Expired Member", "email": "expired@example.com", "role": "volunteer"},
        cookies={SESSION_COOKIE: token},
    )
    invitation = (
        db.query(Invitation)
        .filter(Invitation.org_id == "i_expired", Invitation.email == "expired@example.com")
        .one()
    )
    invitation.expires_at = utcnow() - timedelta(minutes=1)
    db.commit()
    verification = invitations.verify_invitation(invitation.token, db)
    assert verification.valid is False
    db.refresh(invitation)
    assert invitation.status == "expired"

    page = client.get("/a/people", cookies={SESSION_COOKIE: token})

    assert "Expired Member" in page.text
    assert "Expired" in page.text
    assert invitation.token not in page.text
    assert f'action="/a/people/invitations/{invitation.id}/cancel"' in page.text
    cancelled = client.post(
        f"/a/people/invitations/{invitation.id}/cancel", cookies={SESSION_COOKIE: token}
    )
    assert cancelled.status_code == 303
    recreated = client.post(
        "/a/people/invite",
        data={"name": "Expired Member", "email": "expired@example.com", "role": "volunteer"},
        cookies={SESSION_COOKIE: token},
    )
    assert recreated.status_code == 200


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
    assert invitation.token not in client.get("/a/people", cookies={SESSION_COOKIE: token}).text
    _, _, html_body, plain_body = send.call_args.args
    assert f"https://signup.example{path}" in html_body
    assert f"https://signup.example{path}" in plain_body
    client.cookies.clear()
    assert client.get(path).status_code == 200
    accepted = client.post(path, data={"password": "InvitePass123!"})
    assert accepted.status_code == 303
    assert accepted.headers["location"] == "/v/schedule"
