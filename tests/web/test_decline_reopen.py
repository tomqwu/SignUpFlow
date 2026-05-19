"""Overnight B8 — a declined assignment re-opens its slot."""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Assignment, Event
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _vol(client, db, *, org, pid, email):
    seed_person(db, person_id=pid, org_id=org, email=email, roles=["volunteer"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _event(db, org, *, eid="dr_ev"):
    start = datetime.utcnow() + timedelta(days=7)
    db.add(
        Event(
            id=eid,
            org_id=org,
            type="Sunday Service",
            start_time=start,
            end_time=start + timedelta(hours=1),
            extra_data={"role_counts": {"volunteer": 1}},
        )
    )
    db.commit()


def _assign(db, *, eid, pid, status):
    db.add(
        Assignment(
            event_id=eid,
            person_id=pid,
            role="volunteer",
            status=status,
            solution_id=None,
        )
    )
    db.commit()


def test_confirmed_assignment_hides_open_slot(client, db):
    seed_person(db, person_id="dr_a", org_id="dr_o1", email="a@dr.test", roles=["volunteer"])
    tok_b = _vol(client, db, org="dr_o1", pid="dr_b", email="b@dr.test")
    _event(db, "dr_o1")
    _assign(db, eid="dr_ev", pid="dr_a", status="confirmed")
    r = client.get("/v/open", cookies={SESSION_COOKIE: tok_b})
    assert "No open shifts right now" in r.text
    assert "Sunday Service" not in r.text


def test_declined_assignment_reopens_and_is_claimable(client, db):
    seed_person(db, person_id="dr_a2", org_id="dr_o2", email="a2@dr.test", roles=["volunteer"])
    tok_b = _vol(client, db, org="dr_o2", pid="dr_b2", email="b2@dr.test")
    _event(db, "dr_o2")
    _assign(db, eid="dr_ev", pid="dr_a2", status="declined")

    r = client.get("/v/open", cookies={SESSION_COOKIE: tok_b})
    assert "Sunday Service" in r.text and "1 of 1 open" in r.text

    c = client.post(
        "/v/open/dr_ev/claim", data={"role": "volunteer"}, cookies={SESSION_COOKIE: tok_b}
    )
    assert c.status_code == 200
    got = (
        db.query(Assignment)
        .filter(
            Assignment.event_id == "dr_ev",
            Assignment.person_id == "dr_b2",
            Assignment.role == "volunteer",
        )
        .first()
    )
    assert got is not None and got.status == "confirmed"


def test_declined_does_not_consume_claim_capacity(client, db):
    seed_person(db, person_id="dr_a3", org_id="dr_o3", email="a3@dr.test", roles=["volunteer"])
    tok_b = _vol(client, db, org="dr_o3", pid="dr_b3", email="b3@dr.test")
    _event(db, "dr_o3")
    _assign(db, eid="dr_ev", pid="dr_a3", status="declined")
    c = client.post(
        "/v/open/dr_ev/claim", data={"role": "volunteer"}, cookies={SESSION_COOKIE: tok_b}
    )
    assert c.status_code == 200
