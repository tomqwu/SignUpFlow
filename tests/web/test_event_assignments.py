"""Marathon P1.6 — manual assignment editing (per-event assignees)."""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Assignment, Event
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _event(db, org, eid="ev1"):
    start = datetime(2026, 6, 7, 10, 0, 0)
    e = Event(
        id=eid,
        org_id=org,
        type="Sunday Service",
        start_time=start,
        end_time=start + timedelta(hours=1),
    )
    db.add(e)
    db.commit()
    return e


def test_page_admin_only_and_404(client, db):
    seed_person(db, person_id="ea_vol", email="eavol@web.test", roles=["volunteer"])
    v = client.post("/auth/login", data={"email": "eavol@web.test", "password": "WebPass123!"})
    vtok = v.cookies[SESSION_COOKIE]
    assert client.get("/a/events/x/assignments").status_code == 303
    assert client.get("/a/events/x/assignments", cookies={SESSION_COOKIE: vtok}).status_code == 303

    tok = _admin(client, db, org="ea_o1", email="ea1@web.test")
    _event(db, "ea_o1")
    ok = client.get("/a/events/ev1/assignments", cookies={SESSION_COOKIE: tok})
    assert ok.status_code == 200
    assert "Sunday Service" in ok.text
    assert 'id="event-assignments"' in ok.text
    # Unknown event -> 404
    assert (
        client.get("/a/events/nope/assignments", cookies={SESSION_COOKIE: tok}).status_code == 404
    )


def test_add_and_remove_assignee(client, db):
    tok = _admin(client, db, org="ea_o2", email="ea2@web.test")
    _event(db, "ea_o2")
    seed_person(db, person_id="ea_p1", org_id="ea_o2", email="p1@ea.test", roles=["volunteer"])

    r = client.post(
        "/a/events/ev1/assignments/add",
        data={"person_id": "ea_p1", "role": "usher"},
        cookies={SESSION_COOKIE: tok},
    )
    assert r.status_code == 200
    assert "ea_p1" in r.text or "Web User" in r.text
    a = (
        db.query(Assignment)
        .filter(Assignment.event_id == "ev1", Assignment.person_id == "ea_p1")
        .first()
    )
    assert a is not None and a.role == "usher" and a.solution_id is None

    # Double-add rejected.
    dup = client.post(
        "/a/events/ev1/assignments/add",
        data={"person_id": "ea_p1", "role": ""},
        cookies={SESSION_COOKIE: tok},
    )
    assert dup.status_code == 400

    # Remove.
    rem = client.post(
        "/a/events/ev1/assignments/remove",
        data={"person_id": "ea_p1"},
        cookies={SESSION_COOKIE: tok},
    )
    assert rem.status_code == 200
    assert (
        db.query(Assignment)
        .filter(Assignment.event_id == "ev1", Assignment.person_id == "ea_p1")
        .first()
        is None
    )

    # Removing a non-assigned person is graceful.
    again = client.post(
        "/a/events/ev1/assignments/remove",
        data={"person_id": "ea_p1"},
        cookies={SESSION_COOKIE: tok},
    )
    assert again.status_code == 200


def test_cross_org_event_blocked(client, db):
    tok = _admin(client, db, org="ea_o3", email="ea3@web.test")
    seed_person(db, person_id="other_adm", org_id="ea_other", email="o@ea.test", roles=["admin"])
    _event(db, "ea_other", eid="secret_ev")

    assert (
        client.get("/a/events/secret_ev/assignments", cookies={SESSION_COOKIE: tok}).status_code
        == 404
    )
    resp = client.post(
        "/a/events/secret_ev/assignments/add",
        data={"person_id": "other_adm", "role": ""},
        cookies={SESSION_COOKIE: tok},
    )
    assert resp.status_code in (400, 404)
    assert db.query(Assignment).filter(Assignment.event_id == "secret_ev").first() is None
