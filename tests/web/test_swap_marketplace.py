"""Overnight B2 — swap-claim marketplace."""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Assignment, Event
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _login(client, db, *, pid, org, email):
    seed_person(db, person_id=pid, org_id=org, email=email, roles=["volunteer"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _swap_setup(db, org, *, eid, requester, days=10):
    start = datetime.utcnow() + timedelta(days=days)
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
    a = Assignment(event_id=eid, person_id=requester, role="usher", status="swap_requested")
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def test_swaps_requires_auth(client):
    assert client.get("/v/swaps").status_code == 303


def test_claim_transfers_assignment(client, db):
    a_tok = _login(client, db, pid="sm_a", org="sm_o1", email="a@sm.test")
    b_tok = _login(client, db, pid="sm_b", org="sm_o1", email="b@sm.test")
    asg = _swap_setup(db, "sm_o1", eid="sm_ev", requester="sm_a")

    # Requester does NOT see their own request.
    own = client.get("/v/swaps", cookies={SESSION_COOKIE: a_tok})
    assert "Sunday Service" not in own.text

    # Other volunteer sees + covers it.
    page = client.get("/v/swaps", cookies={SESSION_COOKIE: b_tok})
    assert "Sunday Service" in page.text and "requested by" in page.text
    r = client.post(f"/v/swaps/{asg.id}/claim", cookies={SESSION_COOKIE: b_tok})
    assert r.status_code == 200
    db.refresh(asg)
    assert asg.person_id == "sm_b" and asg.status == "confirmed"
    assert "No swap requests to cover" in r.text  # nothing left for B


def test_cannot_claim_if_already_on_event(client, db):
    seed_person(db, person_id="sm_a2", org_id="sm_o2", email="a2@sm.test", roles=["volunteer"])
    b_tok = _login(client, db, pid="sm_b2", org="sm_o2", email="b2@sm.test")
    asg = _swap_setup(db, "sm_o2", eid="sm_ev2", requester="sm_a2")
    # B is already assigned to the same event.
    db.add(Assignment(event_id="sm_ev2", person_id="sm_b2", role="greeter", status="confirmed"))
    db.commit()
    r = client.post(f"/v/swaps/{asg.id}/claim", cookies={SESSION_COOKIE: b_tok})
    assert r.status_code == 400
    assert "already on" in r.text.lower()
    db.refresh(asg)
    assert asg.person_id == "sm_a2"  # untouched


def test_cannot_claim_non_swap(client, db):
    b_tok = _login(client, db, pid="sm_b3", org="sm_o3", email="b3@sm.test")
    seed_person(db, person_id="sm_a3", org_id="sm_o3", email="a3@sm.test", roles=["volunteer"])
    start = datetime.utcnow() + timedelta(days=5)
    db.add(
        Event(
            id="sm_ev3",
            org_id="sm_o3",
            type="Confirmed Ev",
            start_time=start,
            end_time=start + timedelta(hours=1),
        )
    )
    db.commit()
    a = Assignment(event_id="sm_ev3", person_id="sm_a3", role="usher", status="confirmed")
    db.add(a)
    db.commit()
    db.refresh(a)
    r = client.post(f"/v/swaps/{a.id}/claim", cookies={SESSION_COOKIE: b_tok})
    assert r.status_code == 400


def test_open_links_to_swaps(client, db):
    tok = _login(client, db, pid="sm_v", org="sm_o4", email="v@sm.test")
    assert 'href="/v/swaps"' in client.get("/v/open", cookies={SESSION_COOKIE: tok}).text
