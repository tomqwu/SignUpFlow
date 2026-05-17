"""Sprint 11.9 — recurring availability (rrule) editor."""

from __future__ import annotations

from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _login(client, db, email="rr@web.test", pid="rr_user"):
    seed_person(db, person_id=pid, email=email)
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_availability_shows_rrule_section_empty(client, db):
    token = _login(client, db)
    resp = client.get("/v/availability", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Recurring availability" in resp.text
    assert "No recurring rule" in resp.text
    assert "Every Sunday" in resp.text  # preset rendered


def test_set_rrule_via_custom_then_shown(client, db):
    token = _login(client, db, email="rrset@web.test", pid="rrset")
    resp = client.post(
        "/v/availability/rrule",
        data={"rrule": "FREQ=WEEKLY;BYDAY=MO"},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert 'id="rrule-section"' in resp.text
    assert "FREQ=WEEKLY;BYDAY=MO" in resp.text
    assert "Clear recurring rule" in resp.text


def test_set_rrule_via_preset(client, db):
    token = _login(client, db, email="rrp@web.test", pid="rrp")
    resp = client.post(
        "/v/availability/rrule",
        data={"rrule": "FREQ=WEEKLY;BYDAY=SU"},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert "FREQ=WEEKLY;BYDAY=SU" in resp.text


def test_empty_rrule_rejected(client, db):
    token = _login(client, db, email="rre@web.test", pid="rre")
    resp = client.post(
        "/v/availability/rrule",
        data={"rrule": "   "},
        cookies={SESSION_COOKIE: token},
    )
    assert resp.status_code == 200
    assert "form-error" in resp.text
    assert "No recurring rule" in resp.text  # nothing saved


def test_clear_rrule(client, db):
    token = _login(client, db, email="rrc@web.test", pid="rrc")
    client.post(
        "/v/availability/rrule",
        data={"rrule": "FREQ=WEEKLY;BYDAY=FR"},
        cookies={SESSION_COOKIE: token},
    )
    resp = client.post("/v/availability/rrule/clear", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "No recurring rule" in resp.text
    assert "FREQ=WEEKLY;BYDAY=FR" not in resp.text.replace('placeholder="FREQ=WEEKLY;BYDAY=SU"', "")


def test_rrule_endpoints_require_auth(client):
    r1 = client.post("/v/availability/rrule", data={"rrule": "FREQ=DAILY"})
    assert r1.status_code == 303
    r2 = client.post("/v/availability/rrule/clear")
    assert r2.status_code == 303
