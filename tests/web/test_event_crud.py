"""Sprint 11.16 — admin event create / delete."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from api.models import (
    Assignment,
    Event,
    Notification,
    NotificationType,
    RecurringSeries,
)
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


def test_events_create_form_has_roles_field(client, db):
    token = _admin(client, db, org="ec_roles_form", email="ecrf@web.test")
    resp = client.get("/a/events", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Roles needed" in resp.text
    assert 'name="role_name"' in resp.text
    assert 'name="role_count"' in resp.text


def test_create_event_with_roles(client, db):
    token = _admin(client, db, org="ec_roles", email="ecroles@web.test")
    resp = client.post(
        "/a/events/create",
        data={
            "type": "Sunday Service",
            "event_date": "2099-06-07",
            "start_time": "10:00",
            "end_time": "11:30",
            "role_name": ["volunteer", "greeter"],
            "role_count": ["2", "1"],
        },
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    ev = db.query(Event).filter(Event.org_id == "ec_roles", Event.type == "Sunday Service").first()
    assert ev is not None
    assert ev.extra_data.get("role_counts") == {"volunteer": 2, "greeter": 1}


def test_create_event_skips_blank_and_invalid_roles(client, db):
    token = _admin(client, db, org="ec_roles2", email="ecroles2@web.test")
    resp = client.post(
        "/a/events/create",
        data={
            "type": "Partial Roles",
            "event_date": "2099-06-08",
            "start_time": "10:00",
            "end_time": "11:00",
            "role_name": ["volunteer", "", "  ", "usher"],
            "role_count": ["3", "5", "2", "0"],
        },
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    ev = db.query(Event).filter(Event.org_id == "ec_roles2", Event.type == "Partial Roles").first()
    assert ev is not None
    assert ev.extra_data.get("role_counts") == {"volunteer": 3}


def test_create_event_without_roles_has_no_role_counts(client, db):
    token = _admin(client, db, org="ec_roles3", email="ecroles3@web.test")
    resp = client.post(
        "/a/events/create",
        data={
            "type": "No Roles Event",
            "event_date": "2099-06-09",
            "start_time": "10:00",
            "end_time": "11:00",
        },
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    ev = db.query(Event).filter(Event.org_id == "ec_roles3", Event.type == "No Roles Event").first()
    assert ev is not None
    assert "role_counts" not in (ev.extra_data or {})


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


def test_delete_staffed_event_queues_a_cancellation_notice(client, db):
    """The web UI cancels through the same path as the API, notice included."""
    token = _admin(client, db, org="ec_cancel", email="eccancel@web.test")
    event = Event(
        id="ec_cancel_event",
        org_id="ec_cancel",
        type="Sunday Service",
        start_time=datetime(2099, 6, 7, 10, 0),
        end_time=datetime(2099, 6, 7, 11, 30),
    )
    assignment = Assignment(event_id=event.id, person_id="ec_admin", role="usher")
    db.add_all([event, assignment])
    db.commit()

    resp = client.post(f"/a/events/{event.id}/delete", cookies={SESSION_COOKIE: token})

    assert resp.status_code == 200
    notices = (
        db.query(Notification)
        .filter(
            Notification.org_id == "ec_cancel",
            Notification.recipient_id == "ec_admin",
            Notification.type == NotificationType.CANCELLATION,
        )
        .all()
    )
    assert len(notices) == 1


def test_update_event_resets_an_accepted_response(client, db):
    token = _admin(client, db, org="ec_move", email="ecmove@web.test")
    event = Event(
        id="ec_move_event",
        org_id="ec_move",
        type="Sunday Service",
        start_time=datetime(2099, 6, 7, 10, 0),
        end_time=datetime(2099, 6, 7, 11, 30),
    )
    assignment = Assignment(
        event_id=event.id,
        person_id="ec_admin",
        role="usher",
        status="confirmed",
        response_status="accepted",
        commitment_revision=1,
        response_revision=1,
        responded_by_person_id="ec_admin",
        responded_at=utcnow(),
    )
    db.add_all([event, assignment])
    db.commit()

    response = client.post(
        f"/a/events/{event.id}/update",
        data={
            "type": "Sunday Service",
            "event_date": "2099-06-07",
            "start_time": "10:30",
            "end_time": "12:00",
        },
        cookies={SESSION_COOKIE: token},
    )

    assert response.status_code == 200
    db.refresh(event)
    db.refresh(assignment)
    assert event.start_time == datetime(2099, 6, 7, 10, 30)
    assert event.end_time == datetime(2099, 6, 7, 12, 0)
    assert assignment.status == "pending"
    assert assignment.response_status == "pending"
    assert assignment.commitment_revision == 2
    assert assignment.response_revision is None


def test_recurring_event_update_is_scoped_to_one_occurrence(client, db):
    token = _admin(client, db, org="ec_series", email="ecseries@web.test")
    series = RecurringSeries(
        id="ec_series_id",
        org_id="ec_series",
        created_by="ec_series_adm",
        title="Weekly Service",
        duration=90,
        pattern_type="weekly",
        selected_days=["sunday"],
        start_date=date(2099, 6, 7),
        end_condition_type="count",
        occurrence_count=2,
    )
    first = Event(
        id="ec_series_first",
        org_id="ec_series",
        type="Weekly Service",
        start_time=datetime(2099, 6, 7, 10, 0),
        end_time=datetime(2099, 6, 7, 11, 30),
        series_id=series.id,
        occurrence_sequence=1,
    )
    second = Event(
        id="ec_series_second",
        org_id="ec_series",
        type="Weekly Service",
        start_time=datetime(2099, 6, 14, 10, 0),
        end_time=datetime(2099, 6, 14, 11, 30),
        series_id=series.id,
        occurrence_sequence=2,
    )
    db.add_all([series, first, second])
    db.commit()

    events_page = client.get("/a/events", cookies={SESSION_COOKIE: token})
    recurring_page = client.get("/a/recurring", cookies={SESSION_COOKIE: token})
    assert "Edit occurrence" in events_page.text
    assert "Cancel occurrence" in events_page.text
    assert "This change applies to this occurrence only." in events_page.text
    assert "Delete entire series" in recurring_page.text

    response = client.post(
        f"/a/events/{first.id}/update",
        data={
            "type": "Weekly Service",
            "event_date": "2099-06-07",
            "start_time": "10:30",
            "end_time": "12:00",
        },
        cookies={SESSION_COOKIE: token},
    )

    assert response.status_code == 200
    db.refresh(first)
    db.refresh(second)
    assert first.start_time == datetime(2099, 6, 7, 10, 30)
    assert first.is_exception is True
    assert second.start_time == datetime(2099, 6, 14, 10, 0)
    assert second.is_exception is False


def test_invalid_event_update_preserves_existing_values(client, db):
    token = _admin(client, db, org="ec_invalid", email="ecinvalid@web.test")
    event = Event(
        id="ec_invalid_event",
        org_id="ec_invalid",
        type="Practice",
        start_time=datetime(2099, 6, 7, 10, 0),
        end_time=datetime(2099, 6, 7, 11, 30),
    )
    db.add(event)
    db.commit()

    response = client.post(
        f"/a/events/{event.id}/update",
        data={
            "type": "Changed Practice",
            "event_date": "2099-06-07",
            "start_time": "12:00",
            "end_time": "11:00",
        },
        cookies={SESSION_COOKIE: token},
    )

    assert response.status_code == 200
    assert "End time must be after start time" in response.text
    db.refresh(event)
    assert event.type == "Practice"
    assert event.start_time == datetime(2099, 6, 7, 10, 0)
    assert event.end_time == datetime(2099, 6, 7, 11, 30)


def test_event_update_cannot_cross_organizations(client, db):
    token = _admin(client, db, org="ec_intruder", email="ecintruder@web.test")
    event = Event(
        id="ec_private_event",
        org_id="ec_private",
        type="Private Practice",
        start_time=datetime(2099, 6, 7, 10, 0),
        end_time=datetime(2099, 6, 7, 11, 30),
    )
    db.add(event)
    db.commit()

    response = client.post(
        f"/a/events/{event.id}/update",
        data={
            "type": "Changed by another org",
            "event_date": "2099-06-07",
            "start_time": "12:00",
            "end_time": "13:00",
        },
        cookies={SESSION_COOKIE: token},
    )

    assert response.status_code == 200
    assert "Event not found" in response.text
    db.refresh(event)
    assert event.type == "Private Practice"
    assert event.start_time == datetime(2099, 6, 7, 10, 0)
    assert event.end_time == datetime(2099, 6, 7, 11, 30)


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
    assert (
        client.post(
            "/a/events/x/update",
            data={
                "type": "X",
                "event_date": "2099-01-01",
                "start_time": "10:00",
                "end_time": "11:00",
            },
            cookies={SESSION_COOKIE: token},
        ).status_code
        == 303
    )


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
    assert (
        client.post(
            "/a/events/x/update",
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
