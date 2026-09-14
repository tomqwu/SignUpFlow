"""Browser request-integrity coverage for every cookie/form mutation."""

from __future__ import annotations

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from api.main import app
from api.models import Person
from api.utils.rate_limiter import RATE_LIMITS, rate_limiter
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE
from web.request_integrity import CSRF_COOKIE, CSRF_HEADER, is_protected_browser_path

EXPECTED_AUTH_RATE_LIMITS = {
    ("GET", "/auth/invitation/{token}"): "verify_invitation",
    ("POST", "/auth/forgot"): "password_reset",
    ("POST", "/auth/invitation/{token}"): "verify_invitation",
    ("POST", "/auth/login"): "login",
    ("POST", "/auth/reset/{token}"): "password_reset_confirm",
    ("POST", "/auth/signup"): "signup",
}


@pytest.fixture
def raw_client():
    with TestClient(app, follow_redirects=False) as test_client:
        yield test_client


def _csrf_token(client: TestClient, path: str = "/auth/login") -> str:
    response = client.get(path)
    assert response.status_code == 200
    token = response.cookies[CSRF_COOKIE]
    assert f'<meta name="csrf-token" content="{token}">' in response.text
    assert "/web/static/js/request-integrity.js" in response.text
    return token


def _login(client: TestClient, db, *, person_id: str, email: str) -> tuple[Person, str]:
    person = seed_person(db, person_id=person_id, org_id=f"{person_id}-org", email=email)
    csrf_token = _csrf_token(client)
    response = client.post(
        "/auth/login",
        data={"email": email, "password": "WebPass123!"},
        headers={"Origin": "http://testserver", CSRF_HEADER: csrf_token},
    )
    assert response.status_code == 303
    return person, response.cookies[SESSION_COOKIE]


def _profile_payload(name: str) -> dict[str, str]:
    return {"name": name, "timezone": "UTC", "language": "en"}


def test_every_unsafe_browser_route_is_inside_the_protected_surface():
    unsafe = {"POST", "PUT", "PATCH", "DELETE"}
    routes = [
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.methods.intersection(unsafe)
        and not route.path.startswith("/api/")
    ]

    assert routes
    assert all(is_protected_browser_path(route.path) for route in routes)


def test_public_browser_auth_routes_apply_the_api_rate_limit_policies():
    routes = {
        (method, route.path): route
        for route in app.routes
        if isinstance(route, APIRoute)
        for method in route.methods
    }

    for route_key, expected_limit in EXPECTED_AUTH_RATE_LIMITS.items():
        calls = [dependency.call for dependency in routes[route_key].dependant.dependencies]
        assert expected_limit in {
            getattr(call, "rate_limit_type", None) for call in calls
        }, route_key


def test_browser_login_enforces_its_rate_limit(raw_client, monkeypatch):
    monkeypatch.delenv("TESTING", raising=False)
    monkeypatch.delenv("DISABLE_RATE_LIMITS", raising=False)
    rate_limiter.reset("login:testclient")
    csrf_token = _csrf_token(raw_client)
    request = {
        "data": {"email": "nobody@example.test", "password": "WrongPass123!"},
        "headers": {"Origin": "http://testserver", CSRF_HEADER: csrf_token},
    }

    try:
        for _ in range(RATE_LIMITS["login"]["max_requests"]):
            assert raw_client.post("/auth/login", **request).status_code == 401
        assert raw_client.post("/auth/login", **request).status_code == 429
    finally:
        rate_limiter.reset("login:testclient")


def test_missing_csrf_rejects_authenticated_mutation_without_write(raw_client, db):
    person, session = _login(
        raw_client,
        db,
        person_id="csrf-missing",
        email="csrf-missing@example.test",
    )

    response = raw_client.post(
        "/v/profile",
        data=_profile_payload("Unauthorized rename"),
        headers={"Origin": "http://testserver", "HX-Request": "true"},
        cookies={SESSION_COOKIE: session},
    )

    assert response.status_code == 403
    assert response.headers["HX-Retarget"] == "#request-status"
    assert "reload" in response.text.lower()
    db.refresh(person)
    assert person.name == "Web User"


def test_wrong_csrf_rejects_authenticated_mutation_without_write(raw_client, db):
    person, session = _login(
        raw_client,
        db,
        person_id="csrf-wrong",
        email="csrf-wrong@example.test",
    )

    response = raw_client.post(
        "/v/profile",
        data=_profile_payload("Unauthorized rename"),
        headers={
            "Origin": "http://testserver",
            CSRF_HEADER: "not-the-cookie-token",
        },
        cookies={SESSION_COOKIE: session},
    )

    assert response.status_code == 403
    db.refresh(person)
    assert person.name == "Web User"


def test_foreign_origin_rejects_valid_token_without_write(raw_client, db):
    person, session = _login(
        raw_client,
        db,
        person_id="csrf-origin",
        email="csrf-origin@example.test",
    )
    csrf_token = raw_client.cookies[CSRF_COOKIE]

    response = raw_client.post(
        "/v/profile",
        data=_profile_payload("Unauthorized rename"),
        headers={"Origin": "https://attacker.example", CSRF_HEADER: csrf_token},
        cookies={SESSION_COOKIE: session},
    )

    assert response.status_code == 403
    db.refresh(person)
    assert person.name == "Web User"


def test_missing_origin_rejects_valid_token_without_write(raw_client, db):
    person, _session = _login(
        raw_client,
        db,
        person_id="csrf-no-origin",
        email="csrf-no-origin@example.test",
    )
    csrf_token = raw_client.cookies[CSRF_COOKIE]

    response = raw_client.post(
        "/v/profile",
        data=_profile_payload("Unauthorized rename"),
        headers={CSRF_HEADER: csrf_token},
    )

    assert response.status_code == 403
    db.refresh(person)
    assert person.name == "Web User"


def test_forged_matching_cookie_and_header_are_rejected(raw_client, db):
    person, _session = _login(
        raw_client,
        db,
        person_id="csrf-forged",
        email="csrf-forged@example.test",
    )
    raw_client.cookies.set(CSRF_COOKIE, "attacker-controlled")

    response = raw_client.post(
        "/v/profile",
        data=_profile_payload("Unauthorized rename"),
        headers={
            "Origin": "http://testserver",
            CSRF_HEADER: "attacker-controlled",
        },
    )

    assert response.status_code == 403
    assert response.cookies[CSRF_COOKIE] != "attacker-controlled"
    db.refresh(person)
    assert person.name == "Web User"


def test_valid_same_origin_token_allows_authenticated_mutation(raw_client, db):
    person, session = _login(
        raw_client,
        db,
        person_id="csrf-valid",
        email="csrf-valid@example.test",
    )
    csrf_token = raw_client.cookies[CSRF_COOKIE]

    response = raw_client.post(
        "/v/profile",
        data=_profile_payload("Authorized rename"),
        headers={"Origin": "http://testserver", CSRF_HEADER: csrf_token},
        cookies={SESSION_COOKIE: session},
    )

    assert response.status_code == 200
    db.refresh(person)
    assert person.name == "Authorized rename"


def test_login_rejects_missing_token_without_creating_a_session(raw_client, db):
    seed_person(
        db,
        person_id="csrf-login",
        org_id="csrf-login-org",
        email="csrf-login@example.test",
    )

    response = raw_client.post(
        "/auth/login",
        data={"email": "csrf-login@example.test", "password": "WebPass123!"},
        headers={"Origin": "http://testserver"},
    )

    assert response.status_code == 403
    assert SESSION_COOKIE not in response.cookies


def test_csrf_cookie_uses_browser_security_attributes(raw_client):
    response = raw_client.get("/auth/login")
    header = response.headers["set-cookie"]

    assert f"{CSRF_COOKIE}=" in header
    assert "Path=/" in header
    assert "SameSite=lax" in header
    assert "HttpOnly" not in header
    assert "max-age=" in header.lower()


def test_csrf_cookie_is_secure_in_production(raw_client, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")

    response = raw_client.get("/auth/login")

    assert "Secure" in response.headers["set-cookie"]


def test_production_write_fails_closed_without_configured_origin(raw_client, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("FRONTEND_URL", raising=False)
    monkeypatch.delenv("APP_URL", raising=False)
    csrf_token = _csrf_token(raw_client)

    response = raw_client.post(
        "/auth/login",
        data={"email": "nobody@example.test", "password": "WrongPass123!"},
        headers={
            "Cookie": f"{CSRF_COOKIE}={csrf_token}",
            "Origin": "http://testserver",
            CSRF_HEADER: csrf_token,
        },
    )

    assert response.status_code == 403
