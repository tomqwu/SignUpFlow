"""Sprint 11.6 — volunteer assignment detail."""

from __future__ import annotations

from datetime import datetime

from api.models import Assignment, Event
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _login(client, db, email):
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _seed(
    db, person, *, eid="ev_d", etype="Sunday Service", role="usher", status="confirmed", reason=None
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
    a = Assignment(
        event_id=eid,
        person_id=person.id,
        role=role,
        status=status,
        decline_reason=reason,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def test_detail_renders_for_owned_assignment(client, db):
    p = seed_person(db, person_id="d_owner", email="d_owner@web.test")
    a = _seed(db, p, etype="Sunday Service", role="usher")
    token = _login(client, db, "d_owner@web.test")
    resp = client.get(f"/v/schedule/{a.id}", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Sunday Service" in resp.text
    assert "10:00" in resp.text and "11:30" in resp.text
    assert "usher" in resp.text
    assert "confirmed" in resp.text
    assert 'href="/v/schedule"' in resp.text  # back nav


def test_detail_shows_decline_reason(client, db):
    p = seed_person(db, person_id="d_decl", email="d_decl@web.test")
    a = _seed(db, p, status="declined", reason="Out of town that weekend")
    token = _login(client, db, "d_decl@web.test")
    resp = client.get(f"/v/schedule/{a.id}", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Out of town that weekend" in resp.text


def test_detail_404_for_unknown_id(client, db):
    seed_person(db, person_id="d_404", email="d_404@web.test")
    token = _login(client, db, "d_404@web.test")
    resp = client.get("/v/schedule/999999", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 404
    assert "isn't on your schedule" in resp.text


def test_detail_404_for_other_users_assignment(client, db):
    seed_person(db, person_id="d_me", email="d_me@web.test")
    other = seed_person(db, person_id="d_other", email="d_other@web.test")
    a = _seed(db, other, eid="ev_other", etype="Not Mine")
    token = _login(client, db, "d_me@web.test")
    resp = client.get(f"/v/schedule/{a.id}", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 404
    assert "Not Mine" not in resp.text


def test_detail_requires_auth(client):
    resp = client.get("/v/schedule/1")
    assert resp.status_code == 303
    assert resp.headers["location"] == "/auth/login"
