"""Sprint 11.7 — accept / decline / swap HTMX actions."""

from __future__ import annotations

from datetime import datetime

from api.models import Assignment, Event
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _setup(client, db, *, person_id, email, status="pending"):
    p = seed_person(db, person_id=person_id, email=email)
    db.add(
        Event(
            id=f"ev_{person_id}",
            org_id=p.org_id,
            type="Sunday Service",
            start_time=datetime(2026, 6, 7, 10, 0),
            end_time=datetime(2026, 6, 7, 11, 30),
        )
    )
    a = Assignment(
        event_id=f"ev_{person_id}",
        person_id=p.id,
        role="usher",
        status=status,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    login = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return a, login.cookies[SESSION_COOKIE]


def test_accept_updates_status_and_returns_card(client, db):
    a, token = _setup(client, db, person_id="a_acc", email="a_acc@web.test")
    resp = client.post(f"/v/schedule/{a.id}/accept", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert 'id="assignment-card"' in resp.text
    assert "confirmed" in resp.text
    db.refresh(a)
    assert a.status == "confirmed"


def test_decline_requires_reason_and_persists_it(client, db):
    a, token = _setup(client, db, person_id="a_dec", email="a_dec@web.test")
    resp = client.post(
        f"/v/schedule/{a.id}/decline",
        data={"decline_reason": "Away that weekend"},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert "declined" in resp.text
    assert "Away that weekend" in resp.text
    db.refresh(a)
    assert a.status == "declined"
    assert a.decline_reason == "Away that weekend"


def test_decline_without_reason_is_rejected(client, db):
    a, token = _setup(client, db, person_id="a_dec2", email="a_dec2@web.test")
    resp = client.post(
        f"/v/schedule/{a.id}/decline",
        data={"decline_reason": ""},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code in (400, 422)
    db.refresh(a)
    assert a.status == "pending"


def test_swap_request_updates_status(client, db):
    a, token = _setup(client, db, person_id="a_sw", email="a_sw@web.test")
    resp = client.post(
        f"/v/schedule/{a.id}/swap-request",
        data={"note": "Can someone cover?"},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    db.refresh(a)
    assert a.status == "swap_requested"


def test_action_on_other_users_assignment_is_gone(client, db):
    other = seed_person(db, person_id="a_other", email="a_other@web.test")
    db.add(
        Event(
            id="ev_other_act",
            org_id=other.org_id,
            type="Theirs",
            start_time=datetime(2026, 6, 7, 10, 0),
            end_time=datetime(2026, 6, 7, 11, 30),
        )
    )
    a = Assignment(event_id="ev_other_act", person_id=other.id, role="x", status="pending")
    db.add(a)
    db.commit()
    db.refresh(a)

    seed_person(db, person_id="a_me", email="a_me@web.test")
    login = client.post("/auth/login", data={"email": "a_me@web.test", "password": "WebPass123!"})
    token = login.cookies[SESSION_COOKIE]
    resp = client.post(f"/v/schedule/{a.id}/accept", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 404
    assert "isn't on your schedule" in resp.text
    db.refresh(a)
    assert a.status == "pending"


def test_actions_require_auth(client):
    resp = client.post("/v/schedule/1/accept")
    assert resp.status_code == 303
    assert resp.headers["location"] == "/auth/login"
