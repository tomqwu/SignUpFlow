"""Sprint 11.1 — web signup (create org + first admin)."""

from __future__ import annotations

from web.deps import SESSION_COOKIE


def test_signup_page_renders(client):
    resp = client.get("/auth/signup")
    assert resp.status_code == 200
    assert 'name="org_name"' in resp.text
    assert "Create your organization" in resp.text


def test_signup_creates_org_and_admin_then_redirects(client, db):
    resp = client.post(
        "/auth/signup",
        data={
            "org_name": "Hope Community Church",
            "name": "Sarah Kim",
            "email": "sarah@hopechurch.org",
            "password": "StrongPass123!",
        },
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "/a/dashboard"
    assert SESSION_COOKIE in resp.cookies

    # The session works: dashboard loads as admin.
    token = resp.cookies[SESSION_COOKIE]
    dash = client.get("/a/dashboard", cookies={SESSION_COOKIE: token})
    assert dash.status_code == 200
    # 11.12 replaced the placeholder with the real KPI dashboard.
    assert "Dashboard" in dash.text
    assert "Active volunteers" in dash.text


def test_signup_duplicate_email_shows_error(client, db):
    payload = {
        "org_name": "First Org",
        "name": "Admin One",
        "email": "dup@example.com",
        "password": "StrongPass123!",
    }
    first = client.post("/auth/signup", data=payload)
    assert first.status_code == 303

    # Second signup, different org name but same email → API signup
    # raises 409; web surfaces it inline, no cookie.
    payload2 = dict(payload, org_name="Second Org")
    resp = client.post("/auth/signup", data=payload2)
    assert resp.status_code == 409
    assert "already registered" in resp.text.lower()
    assert SESSION_COOKIE not in resp.cookies


def test_signup_short_password_rejected(client, db):
    resp = client.post(
        "/auth/signup",
        data={
            "org_name": "Tiny Pw Org",
            "name": "Pw User",
            "email": "pw@example.com",
            "password": "short",
        },
    )
    # SignupRequest enforces min_length=6 → pydantic ValidationError →
    # surfaced as a form error, not a 500.
    assert resp.status_code in (400, 422)
    assert SESSION_COOKIE not in resp.cookies


def test_signup_redirects_when_already_authenticated(client, db):
    login = client.post(
        "/auth/signup",
        data={
            "org_name": "Already Org",
            "name": "Already In",
            "email": "already@example.com",
            "password": "StrongPass123!",
        },
    )
    token = login.cookies[SESSION_COOKIE]
    resp = client.get("/auth/signup", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 303
    assert resp.headers["location"] == "/a/dashboard"
