"""Overnight B5 — the ICS subscription feed only exposes published work.

Draft solver output (assignment tied to an unpublished Solution) must
stay out of the volunteer's subscribed calendar; manual / self-serve
assignments (no solution) and published-solution assignments appear.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Assignment, Event, Solution
from tests.web.conftest import seed_person


def _event(db, *, eid, org, etype):
    start = datetime(2026, 6, 7, 10, 0, 0)
    db.add(
        Event(
            id=eid,
            org_id=org,
            type=etype,
            start_time=start,
            end_time=start + timedelta(hours=1),
        )
    )


def test_feed_gates_on_publish(client, db):
    p = seed_person(db, person_id="cf_v", org_id="cf_o", email="cf@v.test", roles=["volunteer"])
    p.calendar_token = "cftok123"
    _event(db, eid="cf_pub", org="cf_o", etype="Published Svc")
    _event(db, eid="cf_man", org="cf_o", etype="Manual Svc")
    sol = Solution(
        org_id="cf_o",
        hard_violations=0,
        soft_score=1.0,
        health_score=90.0,
        is_published=False,
    )
    db.add(sol)
    db.commit()
    db.refresh(sol)
    db.add(
        Assignment(
            event_id="cf_pub",
            person_id="cf_v",
            role="usher",
            status="confirmed",
            solution_id=sol.id,
        )
    )
    db.add(
        Assignment(
            event_id="cf_man",
            person_id="cf_v",
            role="greeter",
            status="confirmed",
            solution_id=None,
        )
    )
    db.commit()

    r1 = client.get("/api/v1/calendar/feed/cftok123")
    assert r1.status_code == 200
    assert "Manual Svc" in r1.text  # manual (no solution) → always shown
    assert "Published Svc" not in r1.text  # draft solution → hidden

    sol.is_published = True
    db.commit()

    r2 = client.get("/api/v1/calendar/feed/cftok123")
    assert r2.status_code == 200
    assert "Published Svc" in r2.text  # published → now shown
    assert "Manual Svc" in r2.text


def test_invalid_token_still_404(client, db):
    assert client.get("/api/v1/calendar/feed/nope-xyz").status_code == 404
