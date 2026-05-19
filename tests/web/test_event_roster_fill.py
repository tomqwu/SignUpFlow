"""Overnight B4 — event roster fill view (needed vs filled + inline fill)."""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Assignment, Event
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _event(db, org, *, eid="rev1", role_counts=None):
    start = datetime(2026, 6, 7, 10, 0, 0)
    db.add(
        Event(
            id=eid,
            org_id=org,
            type="Sunday Service",
            start_time=start,
            end_time=start + timedelta(hours=1),
            extra_data={"role_counts": role_counts} if role_counts else None,
        )
    )
    db.commit()


def test_roster_shows_gap(client, db):
    tok = _admin(client, db, org="rf_o1", email="rf1@web.test")
    _event(db, "rf_o1", role_counts={"usher": 2})
    r = client.get("/a/events/rev1/assignments", cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200
    assert 'id="role-coverage"' in r.text
    assert 'data-staffed="no"' in r.text
    assert "0/2 filled" in r.text and "2 needed" in r.text


def test_fill_gap_closes_coverage(client, db):
    tok = _admin(client, db, org="rf_o2", email="rf2@web.test")
    _event(db, "rf_o2", role_counts={"usher": 1})
    seed_person(db, person_id="rf_v", org_id="rf_o2", email="v@rf.test", roles=["volunteer"])
    r = client.post(
        "/a/events/rev1/assignments/add",
        data={"person_id": "rf_v", "role": "usher"},
        cookies={SESSION_COOKIE: tok},
    )
    assert r.status_code == 200
    assert 'data-staffed="yes"' in r.text
    assert "1/1 filled" in r.text and "covered" in r.text
    a = (
        db.query(Assignment)
        .filter(Assignment.event_id == "rev1", Assignment.person_id == "rf_v")
        .first()
    )
    assert a is not None and a.role == "usher"


def test_no_role_counts_hides_coverage(client, db):
    tok = _admin(client, db, org="rf_o3", email="rf3@web.test")
    _event(db, "rf_o3")  # no role_counts
    r = client.get("/a/events/rev1/assignments", cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200
    assert 'id="role-coverage"' not in r.text
