"""Marathon P1.2 — web profile edit + change password."""

from __future__ import annotations

from api.models import Person
from api.security import verify_password
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _user(client, db, *, person_id, org, email, roles):
    seed_person(db, person_id=person_id, org_id=org, email=email, roles=roles)
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_profile_page_has_forms(client, db):
    token = _user(
        client, db, person_id="ac1", org="ac_o1", email="ac1@web.test", roles=["volunteer"]
    )
    resp = client.get("/v/profile", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert 'id="profile-form"' in resp.text
    assert 'id="password-form"' in resp.text


def test_profile_save_updates_person(client, db):
    token = _user(
        client, db, person_id="ac2", org="ac_o2", email="ac2@web.test", roles=["volunteer"]
    )
    resp = client.post(
        "/v/profile",
        data={"name": "Renamed User", "timezone": "America/New_York", "language": "fr"},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert "Profile saved" in resp.text
    p = db.query(Person).filter(Person.id == "ac2").first()
    db.refresh(p)
    assert p.name == "Renamed User"
    assert p.timezone == "America/New_York"
    assert p.language == "fr"


def test_profile_name_required(client, db):
    token = _user(
        client, db, person_id="ac3", org="ac_o3", email="ac3@web.test", roles=["volunteer"]
    )
    resp = client.post(
        "/v/profile",
        data={"name": "  ", "timezone": "", "language": ""},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 400
    assert "required" in resp.text.lower()


def test_password_change_succeeds_and_rehashes(client, db):
    token = _user(
        client, db, person_id="ac4", org="ac_o4", email="ac4@web.test", roles=["volunteer"]
    )
    resp = client.post(
        "/v/account/password",
        data={
            "current_password": "WebPass123!",
            "new_password": "BrandNew456!",
            "confirm_password": "BrandNew456!",
        },
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert "Password changed" in resp.text
    # Session cookie re-issued so the user isn't logged out.
    assert SESSION_COOKIE in resp.cookies
    p = db.query(Person).filter(Person.id == "ac4").first()
    db.refresh(p)
    assert verify_password("BrandNew456!", p.password_hash)
    assert not verify_password("WebPass123!", p.password_hash)


def test_password_change_wrong_current(client, db):
    token = _user(
        client, db, person_id="ac5", org="ac_o5", email="ac5@web.test", roles=["volunteer"]
    )
    resp = client.post(
        "/v/account/password",
        data={
            "current_password": "nope",
            "new_password": "BrandNew456!",
            "confirm_password": "BrandNew456!",
        },
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 400
    assert "incorrect" in resp.text.lower()


def test_password_change_mismatch_and_short(client, db):
    token = _user(
        client, db, person_id="ac6", org="ac_o6", email="ac6@web.test", roles=["volunteer"]
    )
    mismatch = client.post(
        "/v/account/password",
        data={
            "current_password": "WebPass123!",
            "new_password": "BrandNew456!",
            "confirm_password": "different",
        },
        cookies={SESSION_COOKIE: token},
    )
    assert mismatch.status_code == 400
    assert "match" in mismatch.text.lower()

    short = client.post(
        "/v/account/password",
        data={
            "current_password": "WebPass123!",
            "new_password": "abc",
            "confirm_password": "abc",
        },
        cookies={SESSION_COOKIE: token},
    )
    assert short.status_code == 400


def test_account_endpoints_require_auth(client):
    assert client.post("/v/profile", data={"name": "x"}).status_code == 303
    assert (
        client.post(
            "/v/account/password",
            data={
                "current_password": "a",
                "new_password": "bbbbbb",
                "confirm_password": "bbbbbb",
            },
        ).status_code
        == 303
    )


def test_admin_can_use_account_forms(client, db):
    token = _user(client, db, person_id="ac7", org="ac_o7", email="ac7@web.test", roles=["admin"])
    # Admin reaches the same self-service endpoints (session-user gated).
    resp = client.post(
        "/v/profile",
        data={"name": "Admin Renamed", "timezone": "", "language": ""},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    p = db.query(Person).filter(Person.id == "ac7").first()
    db.refresh(p)
    assert p.name == "Admin Renamed"
