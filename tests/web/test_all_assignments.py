"""Marathon P1.10 — admin all-assignments + per-person view."""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Assignment, Event
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _event(db, org, eid):
    start = datetime(2026, 6, 7, 10, 0, 0)
    db.add(
        Event(
            id=eid,
            org_id=org,
            type="Sunday Service",
            start_time=start,
            end_time=start + timedelta(hours=1),
        )
    )
    db.commit()


def _assign(db, eid, pid, role=None, solution_id=None):
    a = Assignment(event_id=eid, person_id=pid, role=role, solution_id=solution_id)
    db.add(a)
    db.commit()


def test_all_assignments_admin_only(client, db):
    seed_person(db, person_id="aa_vol", email="aavol@web.test", roles=["volunteer"])
    login = client.post("/auth/login", data={"email": "aavol@web.test", "password": "WebPass123!"})
    vtok = login.cookies[SESSION_COOKIE]
    assert client.get("/a/assignments").status_code == 303
    assert client.get("/a/assignments", cookies={SESSION_COOKIE: vtok}).status_code == 303

    tok = _admin(client, db, org="aa_o1", email="aa1@web.test")
    resp = client.get("/a/assignments", cookies={SESSION_COOKIE: tok})
    assert resp.status_code == 200
    assert "Assignments" in resp.text
    assert "No assignments" in resp.text  # empty org


def test_lists_and_person_filter(client, db):
    tok = _admin(client, db, org="aa_o2", email="aa2@web.test")
    seed_person(db, person_id="aa_p1", org_id="aa_o2", email="p1@aa.test", roles=["volunteer"])
    seed_person(db, person_id="aa_p2", org_id="aa_o2", email="p2@aa.test", roles=["volunteer"])
    _event(db, "aa_o2", "aa_ev")
    _assign(db, "aa_ev", "aa_p1", role="usher")  # manual
    _assign(db, "aa_ev", "aa_p2", solution_id=None)

    allv = client.get("/a/assignments", cookies={SESSION_COOKIE: tok})
    assert allv.status_code == 200
    assert "Sunday Service" in allv.text
    assert "2 assignments" in allv.text
    assert "manual" in allv.text

    one = client.get("/a/assignments?person_id=aa_p1", cookies={SESSION_COOKIE: tok})
    assert "1 assignment" in one.text
    # Web User is the seeded name for both; ensure the filter narrowed the count.
    assert "2 assignments" not in one.text


def test_dashboard_links_to_assignments(client, db):
    tok = _admin(client, db, org="aa_o3", email="aa3@web.test")
    dash = client.get("/a/dashboard", cookies={SESSION_COOKIE: tok})
    assert 'href="/a/assignments"' in dash.text
