"""Overnight B1 — volunteer self-serve open shifts."""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Assignment, Event
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _vol(client, db, *, org, email, pid):
    seed_person(db, person_id=pid, org_id=org, email=email, roles=["volunteer"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _event(db, org, eid, *, role_counts, days=14):
    start = datetime.utcnow() + timedelta(days=days)
    db.add(
        Event(
            id=eid,
            org_id=org,
            type="Sunday Service",
            start_time=start,
            end_time=start + timedelta(hours=1),
            extra_data={"role_counts": role_counts},
        )
    )
    db.commit()


def test_open_requires_auth(client):
    assert client.get("/v/open").status_code == 303


def test_lists_and_claims_open_role(client, db):
    tok = _vol(client, db, org="os_o1", email="v1@os.test", pid="os_v1")
    _event(db, "os_o1", "os_ev", role_counts={"volunteer": 2})

    page = client.get("/v/open", cookies={SESSION_COOKIE: tok})
    assert page.status_code == 200
    assert "Sunday Service" in page.text
    assert "2 of 2 open" in page.text

    r = client.post(
        "/v/open/os_ev/claim",
        data={"role": "volunteer"},
        cookies={SESSION_COOKIE: tok},
    )
    assert r.status_code == 200
    a = (
        db.query(Assignment)
        .filter(Assignment.event_id == "os_ev", Assignment.person_id == "os_v1")
        .first()
    )
    assert a is not None and a.role == "volunteer" and a.status == "confirmed"
    # Already on the event → no longer offered.
    assert "Sunday Service" not in r.text


def test_capacity_and_double_claim_blocked(client, db):
    tok = _vol(client, db, org="os_o2", email="v2@os.test", pid="os_v2")
    seed_person(db, person_id="os_other", org_id="os_o2", email="o@os.test", roles=["volunteer"])
    _event(db, "os_o2", "os_ev2", role_counts={"usher": 1})
    # Fill the only slot with someone else.
    db.add(Assignment(event_id="os_ev2", person_id="os_other", role="usher", status="confirmed"))
    db.commit()

    r = client.post("/v/open/os_ev2/claim", data={"role": "usher"}, cookies={SESSION_COOKIE: tok})
    assert r.status_code == 400
    assert "filled up" in r.text.lower()
    assert (
        db.query(Assignment)
        .filter(Assignment.event_id == "os_ev2", Assignment.person_id == "os_v2")
        .first()
        is None
    )


def test_past_event_not_open(client, db):
    tok = _vol(client, db, org="os_o3", email="v3@os.test", pid="os_v3")
    start = datetime.utcnow() - timedelta(days=2)
    db.add(
        Event(
            id="os_past",
            org_id="os_o3",
            type="Old",
            start_time=start,
            end_time=start + timedelta(hours=1),
            extra_data={"role_counts": {"volunteer": 1}},
        )
    )
    db.commit()
    page = client.get("/v/open", cookies={SESSION_COOKIE: tok})
    assert "Old" not in page.text
    blocked = client.post(
        "/v/open/os_past/claim", data={"role": "volunteer"}, cookies={SESSION_COOKIE: tok}
    )
    assert blocked.status_code == 400


def test_schedule_links_to_open(client, db):
    tok = _vol(client, db, org="os_o4", email="v4@os.test", pid="os_v4")
    sched = client.get("/v/schedule", cookies={SESSION_COOKIE: tok})
    assert 'href="/v/open"' in sched.text
