"""Marathon P1.8 — analytics drill-down page."""

from __future__ import annotations

import re
from datetime import datetime, timedelta

import pytest

from api.models import Assignment, Event, Person
from tests.web.conftest import seed_person
from web.deps import SESSION_COOKIE


def _admin(client, db, *, org, email):
    seed_person(db, person_id=f"{org}_adm", org_id=org, email=email, roles=["admin"])
    r = client.post("/auth/login", data={"email": email, "password": "WebPass123!"})
    return r.cookies[SESSION_COOKIE]


def test_analytics_admin_only(client, db):
    seed_person(db, person_id="an_vol", email="anvol@web.test", roles=["volunteer"])
    login = client.post("/auth/login", data={"email": "anvol@web.test", "password": "WebPass123!"})
    vtok = login.cookies[SESSION_COOKIE]
    assert client.get("/a/analytics").status_code == 303
    assert client.get("/a/analytics", cookies={SESSION_COOKIE: vtok}).status_code == 303

    tok = _admin(client, db, org="an_o1", email="an1@web.test")
    resp = client.get("/a/analytics", cookies={SESSION_COOKIE: tok})
    assert resp.status_code == 200
    assert "Analytics" in resp.text
    assert "Participation" in resp.text
    assert "Schedule health" in resp.text
    assert "Burnout risk" in resp.text


def test_analytics_filters_applied_and_clamped(client, db):
    tok = _admin(client, db, org="an_o2", email="an2@web.test")
    ok = client.get("/a/analytics?days=7&threshold=2", cookies={SESSION_COOKIE: tok})
    assert ok.status_code == 200
    assert "last 7 days" in ok.text
    assert "≥ 2 in 30 days" in ok.text

    # Out-of-range values fall back to defaults (30 / 4).
    clamped = client.get("/a/analytics?days=9999&threshold=0", cookies={SESSION_COOKIE: tok})
    assert clamped.status_code == 200
    assert "last 30 days" in clamped.text
    assert "≥ 4 in 30 days" in clamped.text


def test_dashboard_links_to_analytics(client, db):
    tok = _admin(client, db, org="an_o3", email="an3@web.test")
    dash = client.get("/a/dashboard", cookies={SESSION_COOKIE: tok})
    assert dash.status_code == 200
    assert 'href="/a/analytics"' in dash.text


# ---------------------------------------------------------------------------
# "Last 30 days" on the dashboard and /a/analytics means the past 30 days.
# A published six-week schedule must not count as recent work or burnout.
# The app clock (api.timeutils.utcnow) is pinned; events are naive UTC.
# ---------------------------------------------------------------------------

PINNED_NOW = datetime(2030, 1, 9, 12, 0)


@pytest.fixture
def scheduled_org(client, db, monkeypatch):
    monkeypatch.setenv("SIGNUPFLOW_ALLOW_TEST_CLOCK", "true")
    monkeypatch.setenv("SIGNUPFLOW_TEST_NOW", PINNED_NOW.isoformat() + "+00:00")
    org = "an_win"
    tok = _admin(client, db, org=org, email="anwin@web.test")
    for pid, name in [("an_recent", "Recent Rita"), ("an_ahead", "Ahead Ari")]:
        db.add(
            Person(
                id=pid,
                org_id=org,
                name=name,
                email=f"{pid}@web.test",
                roles=["volunteer"],
                status="active",
            )
        )
    # Rita served the last four Sundays; Ari is booked for the next six.
    for pid, days in [("an_recent", d) for d in (-2, -9, -16, -23)] + [
        ("an_ahead", d) for d in (5, 12, 19, 26, 33, 40)
    ]:
        start = PINNED_NOW + timedelta(days=days)
        event_id = f"an_evt_{days}"
        db.add(
            Event(
                id=event_id,
                org_id=org,
                type="Sunday",
                start_time=start,
                end_time=start + timedelta(hours=2),
            )
        )
        db.add(Assignment(event_id=event_id, person_id=pid))
    db.commit()
    return tok


def test_dashboard_last_30_days_excludes_future_assignments(client, scheduled_org):
    html = client.get("/a/dashboard", cookies={SESSION_COOKIE: scheduled_org}).text
    most_active = html.split("Most active", 1)[1]
    assert "Recent Rita" in most_active
    assert "Ahead Ari" not in most_active
    assert "1 volunteer(s) at risk" in html


def test_analytics_last_n_days_excludes_future_assignments(client, scheduled_org):
    html = client.get("/a/analytics", cookies={SESSION_COOKIE: scheduled_org}).text
    participation = html.split("Participation · last 30 days", 1)[1].split("Schedule health")[0]
    assert "Recent Rita" in participation
    assert "Ahead Ari" not in participation
    burnout = html.split("Burnout risk", 1)[1]
    assert "Recent Rita" in burnout
    assert "Ahead Ari" not in burnout


def test_analytics_upcoming_events_still_count_the_future(client, scheduled_org):
    html = client.get("/a/analytics", cookies={SESSION_COOKIE: scheduled_org}).text
    health = html.split("Schedule health", 1)[1].split("Burnout risk")[0]
    assert re.search(r'kpi-value">\s*6\s*</div>\s*<div class="kpi-label">Upcoming events', health)
