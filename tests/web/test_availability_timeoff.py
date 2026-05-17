"""Sprint 11.8 — availability time-off CRUD."""

from __future__ import annotations

from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _login(client, db, email="to@web.test", pid="to_user"):
    seed_person(db, person_id=pid, email=email)
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_availability_page_renders(client, db):
    token = _login(client, db)
    resp = client.get("/v/availability", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Availability" in resp.text
    assert 'name="start_date"' in resp.text
    assert "No time-off booked" in resp.text


def test_add_timeoff_then_listed(client, db):
    token = _login(client, db, email="add@web.test", pid="add_user")
    resp = client.post(
        "/v/availability/timeoff",
        data={
            "start_date": "2026-07-01",
            "end_date": "2026-07-05",
            "reason": "Family trip",
        },
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert 'id="timeoff-list"' in resp.text
    assert "Family trip" in resp.text
    assert "JUL" in resp.text.upper()
    assert "No time-off booked" not in resp.text


def test_add_timeoff_end_before_start_rejected(client, db):
    token = _login(client, db, email="bad@web.test", pid="bad_user")
    resp = client.post(
        "/v/availability/timeoff",
        data={"start_date": "2026-07-10", "end_date": "2026-07-01"},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert "form-error" in resp.text
    assert "No time-off booked" in resp.text  # nothing was created


def test_delete_timeoff(client, db):
    token = _login(client, db, email="del@web.test", pid="del_user")
    client.post(
        "/v/availability/timeoff",
        data={"start_date": "2026-08-01", "end_date": "2026-08-01"},
        cookies={SESSION_COOKIE: token},
    )
    page = client.get("/v/availability", cookies={SESSION_COOKIE: token})
    import re

    m = re.search(r"/v/availability/timeoff/(\d+)/delete", page.text)
    assert m, "delete link not rendered"
    tid = m.group(1)

    resp = client.post(
        f"/v/availability/timeoff/{tid}/delete",
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert "No time-off booked" in resp.text


def test_availability_requires_auth(client):
    resp = client.get("/v/availability")
    assert resp.status_code == 303
    assert resp.headers["location"] == "/auth/login"
    resp2 = client.post(
        "/v/availability/timeoff",
        data={"start_date": "2026-07-01", "end_date": "2026-07-02"},
    )
    assert resp2.status_code == 303
