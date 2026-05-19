"""Overnight B7 — bulk-notify the published schedule → inbox."""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Assignment, EmailPreference, Event, Notification, Solution
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def _published_solution(db, org, *, people, eid="bn_ev", published=True):
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
    sol = Solution(
        org_id=org,
        solve_ms=12.0,
        hard_violations=0,
        soft_score=1.0,
        health_score=90.0,
        metrics={},
        is_published=published,
        published_at=datetime.utcnow() if published else None,
    )
    db.add(sol)
    db.commit()
    db.refresh(sol)
    for pid in people:
        seed_person(db, person_id=pid, org_id=org, email=f"{pid}@bn.test", roles=["volunteer"])
        db.add(
            Assignment(
                event_id=eid,
                person_id=pid,
                role="usher",
                status="confirmed",
                solution_id=sol.id,
            )
        )
    db.commit()
    return sol


def test_notify_creates_reminder_per_assignee(client, db):
    tok = _admin(client, db, org="bn_o1", email="bn1@web.test")
    sol = _published_solution(db, "bn_o1", people=["bn_a", "bn_b"])
    r = client.post(f"/a/solution/{sol.id}/notify", cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200
    assert "Reminder sent to 2 assignee(s)" in r.text
    n = (
        db.query(Notification)
        .filter(Notification.org_id == "bn_o1", Notification.type == "reminder")
        .all()
    )
    assert {x.recipient_id for x in n} == {"bn_a", "bn_b"}


def test_notify_honors_email_preferences(client, db):
    tok = _admin(client, db, org="bn_o2", email="bn2@web.test")
    sol = _published_solution(db, "bn_o2", people=["bn_c", "bn_d"])
    # bn_c opted out of reminders.
    db.add(
        EmailPreference(
            person_id="bn_c",
            org_id="bn_o2",
            enabled_types=["assignment"],
            unsubscribe_token="bn-c-tok",
        )
    )
    db.commit()
    r = client.post(f"/a/solution/{sol.id}/notify", cookies={SESSION_COOKIE: tok})
    assert "Reminder sent to 1 assignee(s)" in r.text
    recips = {
        x.recipient_id
        for x in db.query(Notification)
        .filter(Notification.org_id == "bn_o2", Notification.type == "reminder")
        .all()
    }
    assert recips == {"bn_d"}


def test_notify_requires_published(client, db):
    tok = _admin(client, db, org="bn_o3", email="bn3@web.test")
    sol = _published_solution(db, "bn_o3", people=["bn_e"], published=False)
    r = client.post(f"/a/solution/{sol.id}/notify", cookies={SESSION_COOKIE: tok})
    assert r.status_code == 400
    assert "Publish the solution before notifying" in r.text
    assert db.query(Notification).filter(Notification.type == "reminder").count() == 0


def test_notify_unknown_solution_404(client, db):
    tok = _admin(client, db, org="bn_o4", email="bn4@web.test")
    assert client.post("/a/solution/99999/notify", cookies={SESSION_COOKIE: tok}).status_code == 404
