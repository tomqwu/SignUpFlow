"""Marathon P1.9 — recurring-events series UI."""

from __future__ import annotations

from api.models import RecurringSeries
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


WEEKLY = {
    "title": "Sunday Service",
    "duration": "60",
    "location": "",
    "pattern_type": "weekly",
    "selected_days": ["sunday"],
    "start_date": "2026-06-07",
    "start_time": "10:00",
    "end_condition_type": "count",
    "occurrence_count": "8",
    "role_name": "",
    "role_count": "",
}


def test_recurring_admin_only(client, db):
    seed_person(db, person_id="rc_vol", email="rcvol@web.test", roles=["volunteer"])
    login = client.post("/auth/login", data={"email": "rcvol@web.test", "password": "WebPass123!"})
    vtok = login.cookies[SESSION_COOKIE]
    assert client.get("/a/recurring").status_code == 303
    assert client.get("/a/recurring", cookies={SESSION_COOKIE: vtok}).status_code == 303

    tok = _admin(client, db, org="rc_o1", email="rc1@web.test")
    resp = client.get("/a/recurring", cookies={SESSION_COOKIE: tok})
    assert resp.status_code == 200
    assert 'id="recurring-list"' in resp.text
    assert "New series" in resp.text


def test_create_weekly_series(client, db):
    tok = _admin(client, db, org="rc_o2", email="rc2@web.test")
    r = client.post("/a/recurring/create", data=WEEKLY, cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200, r.text
    assert "Sunday Service" in r.text
    s = db.query(RecurringSeries).filter(RecurringSeries.org_id == "rc_o2").first()
    assert s is not None
    assert s.pattern_type == "weekly"
    assert s.selected_days == ["sunday"]


def test_create_validation(client, db):
    tok = _admin(client, db, org="rc_o3", email="rc3@web.test")
    no_title = client.post(
        "/a/recurring/create",
        data={**WEEKLY, "title": "  "},
        cookies={SESSION_COOKIE: tok},
    )
    assert no_title.status_code == 400
    assert "title is required" in no_title.text.lower()

    bad_date = client.post(
        "/a/recurring/create",
        data={**WEEKLY, "start_date": "not-a-date"},
        cookies={SESSION_COOKIE: tok},
    )
    assert bad_date.status_code == 400


def test_create_monthly_and_delete(client, db):
    tok = _admin(client, db, org="rc_o4", email="rc4@web.test")
    monthly = {
        "title": "First Sunday Potluck",
        "duration": "90",
        "location": "Hall",
        "pattern_type": "monthly",
        "weekday_position": "first",
        "weekday_name": "sunday",
        "start_date": "2026-06-07",
        "start_time": "12:00",
        "end_condition_type": "count",
        "occurrence_count": "6",
        "role_name": "",
        "role_count": "",
    }
    r = client.post("/a/recurring/create", data=monthly, cookies={SESSION_COOKIE: tok})
    assert r.status_code == 200
    s = db.query(RecurringSeries).filter(RecurringSeries.org_id == "rc_o4").first()
    assert s.pattern_type == "monthly" and s.weekday_position == "first"

    d = client.post(f"/a/recurring/{s.id}/delete", cookies={SESSION_COOKIE: tok})
    assert d.status_code == 200
    assert (
        db.query(RecurringSeries)
        .filter(RecurringSeries.id == s.id, RecurringSeries.active.is_(True))
        .first()
        is None
    )
