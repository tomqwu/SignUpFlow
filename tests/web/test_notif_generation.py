"""Marathon P2.17 — publishing a solution emits inbox notifications."""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Assignment, Event, Notification, Solution
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _login(client, email):
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_publish_creates_inbox_notifications(client, db):
    seed_person(db, person_id="ng_adm", org_id="ng_o1", email="ngadm@web.test", roles=["admin"])
    seed_person(db, person_id="ng_vol", org_id="ng_o1", email="ngvol@web.test", roles=["volunteer"])
    sol = Solution(
        org_id="ng_o1", hard_violations=0, soft_score=1.0, health_score=90.0, solve_ms=5.0
    )
    db.add(sol)
    db.commit()
    db.refresh(sol)
    start = datetime(2026, 6, 7, 10, 0, 0)
    db.add(
        Event(
            id="ng_ev",
            org_id="ng_o1",
            type="Sunday Service",
            start_time=start,
            end_time=start + timedelta(hours=1),
        )
    )
    db.commit()
    db.add(
        Assignment(
            event_id="ng_ev",
            person_id="ng_vol",
            role="usher",
            solution_id=sol.id,
            status="confirmed",
        )
    )
    db.commit()

    atok = _login(client, "ngadm@web.test")
    pub = client.post(f"/a/solution/{sol.id}/publish", cookies={SESSION_COOKIE: atok})
    assert pub.status_code == 200
    assert "Published" in pub.text

    notif = (
        db.query(Notification)
        .filter(
            Notification.org_id == "ng_o1",
            Notification.recipient_id == "ng_vol",
            Notification.type == "assignment",
        )
        .first()
    )
    assert notif is not None
    assert notif.event_id == "ng_ev"

    # The volunteer sees it in their inbox (P1.5).
    vtok = _login(client, "ngvol@web.test")
    inbox = client.get("/v/inbox", cookies={SESSION_COOKIE: vtok})
    assert inbox.status_code == 200
    assert "New assignment" in inbox.text
    assert "1 unread" in inbox.text


def test_publish_without_assignments_still_ok(client, db):
    seed_person(db, person_id="ng_a2", org_id="ng_o2", email="ng2@web.test", roles=["admin"])
    sol = Solution(
        org_id="ng_o2", hard_violations=0, soft_score=1.0, health_score=90.0, solve_ms=5.0
    )
    db.add(sol)
    db.commit()
    db.refresh(sol)
    tok = _login(client, "ng2@web.test")
    pub = client.post(f"/a/solution/{sol.id}/publish", cookies={SESSION_COOKIE: tok})
    assert pub.status_code == 200
    assert db.query(Notification).filter(Notification.org_id == "ng_o2").first() is None
