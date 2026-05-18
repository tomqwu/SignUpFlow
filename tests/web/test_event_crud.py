"""Sprint 11.16 — admin event create / delete."""

from __future__ import annotations

from datetime import datetime, timedelta

from api.models import Event
from api.timeutils import utcnow
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org="ec_org", email="ecadmin@web.test"):
    seed_person(db, person_id="ec_admin", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_events_page_has_create_form(client, db):
    token = _admin(client, db)
    resp = client.get("/a/events", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "New event" in resp.text
    assert 'hx-post="/a/events/create"' in resp.text


def test_create_event(client, db):
    token = _admin(client, db, org="ec_org2", email="ecadmin2@web.test")
    resp = client.post(
        "/a/events/create",
        data={
            "type": "Sunday 10am Service",
            "event_date": "2099-06-07",
            "start_time": "10:00",
            "end_time": "11:30",
        },
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert 'id="events-list"' in resp.text
    assert "Sunday 10am Service" in resp.text
    ev = (
        db.query(Event)
        .filter(Event.org_id == "ec_org2", Event.type == "Sunday 10am Service")
        .first()
    )
    assert ev is not None
    assert ev.start_time == datetime(2099, 6, 7, 10, 0)
    assert ev.end_time == datetime(2099, 6, 7, 11, 30)


def test_create_event_end_before_start_rejected(client, db):
    token = _admin(client, db, org="ec_org3", email="ecadmin3@web.test")
    resp = client.post(
        "/a/events/create",
        data={
            "type": "Bad Event",
            "event_date": "2099-06-07",
            "start_time": "11:00",
            "end_time": "10:00",
        },
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert "form-error" in resp.text
    assert (
        db.query(Event).filter(Event.org_id == "ec_org3", Event.type == "Bad Event").first() is None
    )


def test_delete_event(client, db):
    token = _admin(client, db, org="ec_org4", email="ecadmin4@web.test")
    db.add(
        Event(
            id="ec_del",
            org_id="ec_org4",
            type="Doomed Event",
            start_time=utcnow() + timedelta(days=2),
            end_time=utcnow() + timedelta(days=2, hours=1),
        )
    )
    db.commit()
    resp = client.post("/a/events/ec_del/delete", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Doomed Event" not in resp.text
    assert db.query(Event).filter(Event.id == "ec_del").first() is None


def test_event_crud_requires_admin(client, db):
    seed_person(db, person_id="ec_vol", email="ecvol@web.test", roles=["volunteer"])
    login = client.post(
        "/auth/login",
        data={"email": "ecvol@web.test", "password": "WebPass123!"},
    )
    token = login.cookies[SESSION_COOKIE]
    r = client.post(
        "/a/events/create",
        data={
            "type": "X",
            "event_date": "2099-01-01",
            "start_time": "10:00",
            "end_time": "11:00",
        },
        cookies={SESSION_COOKIE: token},
    )
    assert r.status_code == 303


def test_event_crud_requires_auth(client):
    assert (
        client.post(
            "/a/events/create",
            data={
                "type": "X",
                "event_date": "2099-01-01",
                "start_time": "10:00",
                "end_time": "11:00",
            },
        ).status_code
        == 303
    )
    assert client.post("/a/events/x/delete").status_code == 303
