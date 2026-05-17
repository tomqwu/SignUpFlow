"""Sprint 11.5 — volunteer schedule list (real data)."""

from __future__ import annotations

from datetime import datetime

from api.models import Assignment, Event
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _login(client, db, **kw):
    seed_person(db, **kw)
    email = kw.get("email", "user@web.test")
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _seed_assignment(
    db, person, *, eid="evt1", etype="Sunday Service", role="usher", status="confirmed"
):
    db.add(
        Event(
            id=eid,
            org_id=person.org_id,
            type=etype,
            start_time=datetime(2026, 6, 7, 10, 0),
            end_time=datetime(2026, 6, 7, 11, 30),
        )
    )
    db.add(
        Assignment(
            event_id=eid,
            person_id=person.id,
            role=role,
            status=status,
        )
    )
    db.commit()


def test_schedule_empty_state(client, db):
    token = _login(client, db, person_id="p_empty", email="empty@web.test")
    resp = client.get("/v/schedule", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "No assignments yet" in resp.text


def test_schedule_lists_assignment_with_event_details(client, db):
    person = seed_person(db, person_id="p_sched", email="sched@web.test")
    _seed_assignment(db, person, etype="Sunday Service", role="usher")
    login = client.post(
        "/auth/login",
        data={"email": "sched@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]

    resp = client.get("/v/schedule", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Sunday Service" in resp.text
    assert "10:00" in resp.text and "11:30" in resp.text
    assert "usher" in resp.text
    assert "confirmed" in resp.text
    # Row links to the (future) detail page.
    assert "/v/schedule/" in resp.text


def test_schedule_requires_auth(client):
    resp = client.get("/v/schedule")
    assert resp.status_code == 303
    assert resp.headers["location"] == "/auth/login"


def test_schedule_scoped_to_caller(client, db):
    seed_person(db, person_id="me_sched", email="me@web.test")
    other = seed_person(db, person_id="other_sched", email="other@web.test")
    _seed_assignment(db, other, eid="evt_other", etype="Not Mine")
    login = client.post(
        "/auth/login",
        data={"email": "me@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    resp = client.get("/v/schedule", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Not Mine" not in resp.text
    assert "No assignments yet" in resp.text
