"""Marathon P1.11 — swap-request review."""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Assignment, Event
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _seed_swap(db, org, *, status="swap_requested"):
    seed_person(db, person_id=f"{org}_p", org_id=org, email=f"p@{org}.test", roles=["volunteer"])
    start = datetime(2026, 6, 7, 10, 0, 0)
    db.add(
        Event(
            id=f"{org}_ev",
            org_id=org,
            type="Sunday Service",
            start_time=start,
            end_time=start + timedelta(hours=1),
        )
    )
    db.commit()
    a = Assignment(event_id=f"{org}_ev", person_id=f"{org}_p", role="usher", status=status)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def test_swaps_admin_only(client, db):
    seed_person(db, person_id="sw_vol", email="swvol@web.test", roles=["volunteer"])
    login = client.post("/auth/login", data={"email": "swvol@web.test", "password": "WebPass123!"})
    vtok = login.cookies[SESSION_COOKIE]
    assert client.get("/a/swaps").status_code == 303
    assert client.get("/a/swaps", cookies={SESSION_COOKIE: vtok}).status_code == 303

    tok = _admin(client, db, org="sw_o1", email="sw1@web.test")
    resp = client.get("/a/swaps", cookies={SESSION_COOKIE: tok})
    assert resp.status_code == 200
    assert "Swap requests" in resp.text
    assert "No swap requests" in resp.text  # none yet


def test_only_swap_requested_listed(client, db):
    tok = _admin(client, db, org="sw_o2", email="sw2@web.test")
    _seed_swap(db, "sw_o2", status="confirmed")  # not a swap
    resp = client.get("/a/swaps", cookies={SESSION_COOKIE: tok})
    assert "No swap requests" in resp.text


def test_deny_keeps_assignment(client, db):
    tok = _admin(client, db, org="sw_o3", email="sw3@web.test")
    a = _seed_swap(db, "sw_o3")
    listed = client.get("/a/swaps", cookies={SESSION_COOKIE: tok})
    assert "Sunday Service" in listed.text

    r = client.post(f"/a/swaps/{a.id}/deny", cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200
    db.refresh(a)
    assert a.status == "confirmed"
    assert "No swap requests" in r.text  # no longer pending


def test_approve_unassigns(client, db):
    tok = _admin(client, db, org="sw_o4", email="sw4@web.test")
    a = _seed_swap(db, "sw_o4")
    aid = a.id
    r = client.post(f"/a/swaps/{aid}/approve", cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200
    assert db.query(Assignment).filter(Assignment.id == aid).first() is None
    assert "No swap requests" in r.text


def test_dashboard_links_to_swaps(client, db):
    tok = _admin(client, db, org="sw_o5", email="sw5@web.test")
    dash = client.get("/a/dashboard", cookies={SESSION_COOKIE: tok})
    assert 'href="/a/swaps"' in dash.text
