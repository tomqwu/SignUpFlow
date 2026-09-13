"""Deferred commercial pages stay out of the default web workflow."""

from api.core.config import settings
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin_cookie(client, db):
    seed_person(
        db,
        person_id="commercial_admin",
        org_id="commercial_web",
        email="commercial@web.test",
        roles=["admin"],
    )
    response = client.post(
        "/auth/login",
        data={"email": "commercial@web.test", "password": "WebPass123!"},
    )
    return response.cookies[SESSION_COOKIE]


def test_commercial_pages_and_navigation_are_disabled_by_default(client, db, monkeypatch):
    monkeypatch.setattr(settings, "BILLING_ENABLED", False)
    login = client.get("/auth/login")
    cookie = _admin_cookie(client, db)

    dashboard = client.get("/a/dashboard", cookies={SESSION_COOKIE: cookie})

    assert dashboard.status_code == 200
    assert login.status_code == 200
    assert 'href="/a/billing"' not in dashboard.text
    assert 'href="/pricing"' not in login.text
    assert client.get("/a/billing", cookies={SESSION_COOKIE: cookie}).status_code == 404
    assert client.get("/pricing").status_code == 404
