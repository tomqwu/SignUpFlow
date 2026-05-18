"""Sprint 11.11 — profile calendar subscription + token reset."""

from __future__ import annotations

import re

from api.models import Person
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _login(client, db, email="cal@web.test", pid="cal_user"):
    seed_person(db, person_id=pid, email=email)
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_profile_shows_calendar_url(client, db):
    token = _login(client, db)
    resp = client.get("/v/profile", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert "Subscription URL" in resp.text
    assert "/calendar/feed/" in resp.text
    assert "Reset link" in resp.text
    # Token was generated lazily.
    p = db.query(Person).filter(Person.id == "cal_user").first()
    assert p.calendar_token


def test_calendar_reset_rotates_token(client, db):
    token = _login(client, db, email="calr@web.test", pid="calr")
    page = client.get("/v/profile", cookies={SESSION_COOKIE: token})
    old = re.search(r"/calendar/feed/([A-Za-z0-9_\-]+)", page.text).group(1)

    resp = client.post("/v/profile/calendar/reset", cookies={SESSION_COOKIE: token})
    assert resp.status_code == 200
    assert 'id="calendar-section"' in resp.text
    new = re.search(r"/calendar/feed/([A-Za-z0-9_\-]+)", resp.text).group(1)
    assert new != old
    p = db.query(Person).filter(Person.id == "calr").first()
    db.refresh(p)
    assert p.calendar_token == new


def test_calendar_url_stable_across_loads(client, db):
    token = _login(client, db, email="cals@web.test", pid="cals")
    r1 = client.get("/v/profile", cookies={SESSION_COOKIE: token})
    r2 = client.get("/v/profile", cookies={SESSION_COOKIE: token})
    t1 = re.search(r"/calendar/feed/([A-Za-z0-9_\-]+)", r1.text).group(1)
    t2 = re.search(r"/calendar/feed/([A-Za-z0-9_\-]+)", r2.text).group(1)
    assert t1 == t2  # not regenerated on every view


def test_calendar_reset_requires_auth(client):
    resp = client.post("/v/profile/calendar/reset")
    assert resp.status_code == 303
    assert resp.headers["location"] == "/auth/login"
