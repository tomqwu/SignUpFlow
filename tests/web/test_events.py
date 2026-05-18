"""Sprint 11.15 — admin events list."""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Event
from api.timeutils import utcnow
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org="e_org", email="eadmin@web.test"):
    seed_person(db, person_id="e_admin", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_events_empty(client, db):
    token = _admin(client, db)
    resp = client.get("/a/events", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Events" in resp.text
    assert "No upcoming events" in resp.text
    assert "No past events" in resp.text


def test_events_split_upcoming_past(client, db):
    token = _admin(client, db, org="e_org2", email="eadmin2@web.test")
    now = utcnow()
    db.add(
        Event(
            id="e_up",
            org_id="e_org2",
            type="Future Service",
            start_time=now + timedelta(days=7),
            end_time=now + timedelta(days=7, hours=1),
        )
    )
    db.add(
        Event(
            id="e_past",
            org_id="e_org2",
            type="Old Meeting",
            start_time=now - timedelta(days=7),
            end_time=now - timedelta(days=7) + timedelta(hours=1),
        )
    )
    db.commit()
    resp = client.get("/a/events", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Future Service" in resp.text
    assert "Old Meeting" in resp.text
    # Upcoming section appears before Past in the document.
    assert resp.text.index("Future Service") < resp.text.index("Old Meeting")


def test_events_scoped_to_org(client, db):
    token = _admin(client, db, org="e_org3", email="eadmin3@web.test")
    db.add(
        Event(
            id="e_other",
            org_id="other_org",
            type="Not Mine Event",
            start_time=datetime(2099, 1, 1, 10),
            end_time=datetime(2099, 1, 1, 11),
        )
    )
    db.commit()
    resp = client.get("/a/events", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Not Mine Event" not in resp.text


def test_events_requires_admin(client, db):
    seed_person(db, person_id="e_vol", email="evol@web.test", roles=["volunteer"])
    login = client.post(
        "/auth/login",
        data={"email": "evol@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    resp = client.get("/a/events", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 303


def test_events_requires_auth(client):
    assert client.get("/a/events").status_code == 303
