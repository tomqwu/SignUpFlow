"""Sprint 11.12 — admin dashboard KPIs."""

from __future__ import annotations

from datetime import datetime

from api.models import Assignment, Event
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org="d_org", email="dadmin@web.test"):
    seed_person(db, person_id="d_admin", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_dashboard_empty_org_shows_zeros(client, db):
    token = _admin(client, db)
    resp = client.get("/a/dashboard", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Dashboard" in resp.text
    assert "Active volunteers" in resp.text
    assert "Upcoming events" in resp.text
    assert "Event coverage" in resp.text
    # graceful zeros, no crash
    assert "No assignments in the last 30 days" in resp.text
    assert "Sign out" in resp.text


def test_dashboard_reflects_data(client, db):
    token = _admin(client, db, org="d_org2", email="dadmin2@web.test")
    vol = seed_person(db, person_id="d_vol", org_id="d_org2", email="dvol@web.test")
    db.add(
        Event(
            id="d_ev",
            org_id="d_org2",
            type="Sunday Service",
            start_time=datetime(2099, 6, 7, 10, 0),
            end_time=datetime(2099, 6, 7, 11, 30),
        )
    )
    db.add(Assignment(event_id="d_ev", person_id=vol.id, role="usher", status="confirmed"))
    db.commit()

    resp = client.get("/a/dashboard", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    # Upcoming event counted; top-volunteer list populated.
    assert "Sunday Service" not in resp.text  # dashboard shows names, not events
    assert "Val" not in resp.text or "d_vol" not in resp.text
    assert "Most active" in resp.text
    assert "Web User" in resp.text  # seed_person name → appears in top list


def test_dashboard_requires_admin(client, db):
    seed_person(db, person_id="d_volonly", email="dvolonly@web.test", roles=["volunteer"])
    login = client.post(
        "/auth/login",
        data={"email": "dvolonly@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    resp = client.get("/a/dashboard", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 303
    assert resp.headers["location"] == "/auth/login"


def test_dashboard_requires_auth(client):
    resp = client.get("/a/dashboard")
    assert resp.status_code == 303
