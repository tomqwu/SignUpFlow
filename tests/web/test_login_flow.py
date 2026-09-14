"""Sprint 11.0 — cookie auth + shell render end-to-end."""

from __future__ import annotations

from jose import jwt

from api.security import ALGORITHM, SECRET_KEY, create_access_token
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def test_login_page_renders(client):
    resp = client.get("/auth/login")
    assert resp.status_code == 200
    assert "SIGNUP" in resp.text
    assert 'name="email"' in resp.text


def test_root_redirects_to_login_when_anonymous(client):
    resp = client.get("/")
    assert resp.status_code == 303
    assert resp.headers["location"] == "/auth/login"


def test_protected_page_redirects_when_anonymous(client):
    resp = client.get("/v/schedule")
    assert resp.status_code == 303
    assert resp.headers["location"] == "/auth/login"


def test_login_bad_credentials_returns_401_with_error(client, db):
    seed_person(db)
    resp = client.post(
        "/auth/login",
        data={"email": "user@web.test", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.text
    assert SESSION_COOKIE not in resp.cookies


def test_volunteer_login_sets_cookie_and_redirects_to_schedule(client, db):
    seed_person(db, roles=["volunteer"])
    resp = client.post(
        "/auth/login",
        data={"email": "user@web.test", "password": "WebPass123!"},
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "/v/schedule"
    assert SESSION_COOKIE in resp.cookies
    payload = jwt.decode(resp.cookies[SESSION_COOKIE], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["org_id"] == "web_org"


def test_admin_login_redirects_to_dashboard(client, db):
    seed_person(db, person_id="admin1", email="admin@web.test", roles=["admin"])
    resp = client.post(
        "/auth/login",
        data={"email": "admin@web.test", "password": "WebPass123!"},
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "/a/dashboard"


def test_authenticated_session_can_load_schedule(client, db):
    seed_person(db, roles=["volunteer"])
    login = client.post(
        "/auth/login",
        data={"email": "user@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    resp = client.get("/v/schedule", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    # 11.5 replaced the placeholder with the real schedule page; a fresh
    # user with no assignments sees the empty state.
    assert "Schedule" in resp.text
    assert "No assignments yet" in resp.text


def test_session_cookie_requires_matching_tenant_claim(client, db):
    person = seed_person(db, roles=["volunteer"])
    for claims in (
        {"sub": person.id},
        {"sub": person.id, "org_id": "foreign-org"},
    ):
        token = create_access_token(claims)
        resp = client.get("/v/schedule", cookies={SESSION_COOKIE: token})
        assert resp.status_code == 303
        assert resp.headers["location"] == "/auth/login"


def test_inactive_membership_cannot_login_or_continue_session(client, db):
    person = seed_person(db, roles=["volunteer"])
    login = client.post(
        "/auth/login",
        data={"email": person.email, "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    person.status = "inactive"
    db.commit()

    rejected_login = client.post(
        "/auth/login",
        data={"email": person.email, "password": "WebPass123!"},
    )
    rejected_session = client.get("/v/schedule", cookies={SESSION_COOKIE: token})

    assert rejected_login.status_code == 401
    assert SESSION_COOKIE not in rejected_login.cookies
    assert rejected_session.status_code == 303
    assert rejected_session.headers["location"] == "/auth/login"


def test_volunteer_cannot_load_admin_dashboard(client, db):
    seed_person(db, roles=["volunteer"])
    login = client.post(
        "/auth/login",
        data={"email": "user@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    resp = client.get("/a/dashboard", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 303
    assert resp.headers["location"] == "/auth/login"


def test_logout_clears_cookie(client, db):
    seed_person(db)
    login = client.post(
        "/auth/login",
        data={"email": "user@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    resp = client.post("/auth/logout", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 303
    assert resp.headers["location"] == "/auth/login"
    # Cookie deleted: Set-Cookie with empty value / past expiry.
    assert SESSION_COOKIE in resp.headers.get("set-cookie", "")
