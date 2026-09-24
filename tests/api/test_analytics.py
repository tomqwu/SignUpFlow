"""Tests for /api/v1/analytics — covers the previously zero-test analytics router.

Sprint 4 PR 4.5d gated all three endpoints behind
`Depends(get_current_admin_user)` + `verify_org_member`. Baseline
smoke tests now authenticate as an admin so they exercise the same
happy paths they always did.
"""

from datetime import datetime, timedelta

import pytest

from api.models import Assignment, Event, Person
from tests.api.conftest import auth_headers, seed_org, seed_user


@pytest.fixture
def org_id(client):
    org = "analytics-test-org"
    seed_org(client, org)
    seed_user(client, org, email="admin@a.org", name="Admin", password="AdminPass1!")
    return org


@pytest.fixture
def admin_hdrs(client, org_id):
    return auth_headers(client, email="admin@a.org", password="AdminPass1!")


@pytest.mark.no_mock_auth
class TestVolunteerStats:
    def test_returns_baseline_for_empty_org(self, client, db, org_id, admin_hdrs):
        resp = client.get(
            f"/api/v1/analytics/{org_id}/volunteer-stats",
            headers=admin_hdrs,
        )
        assert resp.status_code == 200
        body = resp.json()
        # Whatever the schema, endpoint must succeed and return JSON
        assert isinstance(body, dict)

    def test_403_for_unknown_org(self, client, db, org_id, admin_hdrs):
        # Admin-of-org-A hitting unknown org must be rejected before any DB read.
        resp = client.get(
            "/api/v1/analytics/no-such-org/volunteer-stats",
            headers=admin_hdrs,
        )
        assert resp.status_code == 403

    def test_accepts_days_query_param(self, client, db, org_id, admin_hdrs):
        resp = client.get(
            f"/api/v1/analytics/{org_id}/volunteer-stats?days=7",
            headers=admin_hdrs,
        )
        assert resp.status_code == 200


@pytest.mark.no_mock_auth
class TestScheduleHealth:
    def test_returns_for_org(self, client, db, org_id, admin_hdrs):
        resp = client.get(
            f"/api/v1/analytics/{org_id}/schedule-health",
            headers=admin_hdrs,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, dict)


@pytest.mark.no_mock_auth
class TestBurnoutRisk:
    def test_returns_for_org(self, client, db, org_id, admin_hdrs):
        resp = client.get(
            f"/api/v1/analytics/{org_id}/burnout-risk",
            headers=admin_hdrs,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, dict | list)

    def test_no_assignments_means_no_at_risk(self, client, db, org_id, admin_hdrs):
        """An org with zero events/assignments cannot have burnout risk by definition."""
        resp = client.get(
            f"/api/v1/analytics/{org_id}/burnout-risk",
            headers=admin_hdrs,
        )
        assert resp.status_code == 200
        body = resp.json()
        # Whether `at_risk_volunteers` is absent or `[]`, the value must be falsy.
        if isinstance(body, dict) and "at_risk_volunteers" in body:
            assert not body["at_risk_volunteers"]


# ---------------------------------------------------------------------------
# Time windows. "Last N days" means [now - N days, now]; schedule health is
# about what's still ahead. The app clock is pinned (api.timeutils.utcnow)
# far from the real clock so a stray local datetime.now() cannot pass.
# Event.start_time is stored as naive UTC.
# ---------------------------------------------------------------------------

PINNED_NOW = datetime(2030, 1, 9, 12, 0)


@pytest.fixture
def pinned_clock(monkeypatch):
    monkeypatch.setenv("SIGNUPFLOW_ALLOW_TEST_CLOCK", "true")
    monkeypatch.setenv("SIGNUPFLOW_TEST_NOW", PINNED_NOW.isoformat() + "+00:00")
    return PINNED_NOW


def _person(db, org_id: str, person_id: str, name: str) -> None:
    db.add(
        Person(
            id=person_id,
            org_id=org_id,
            name=name,
            email=f"{person_id}@a.org",
            roles=["volunteer"],
            status="active",
        )
    )


def _serve(db, org_id: str, person_id: str, offset: timedelta) -> None:
    """One assignment for `person_id` on an event starting at now + offset."""
    start = PINNED_NOW + offset
    event_id = f"evt_{person_id}_{int(offset.total_seconds())}"
    if db.get(Event, event_id) is None:
        db.add(
            Event(
                id=event_id,
                org_id=org_id,
                type="Sunday Service",
                start_time=start,
                end_time=start + timedelta(hours=2),
            )
        )
    db.add(Assignment(event_id=event_id, person_id=person_id))


@pytest.fixture
def windowed_org(db, org_id, pinned_clock):
    """Assignments in the window, before it and in the future.

    - Heavy: 4 in the last 30 days (-1, -5, -10, -20 days)
    - Planned: 1 in the window (-3 days), 1 before it (-40 days) and 4 ahead
      (+2 hours, +3, +10, +17 days). Four upcoming Sundays are not burnout.
    - Tomorrow: only future assignments (+1, +8, +15, +22 days)
    - Lapsed: only an assignment before the window (-45 days)
    - Just now: one event that started two hours ago
    """
    for pid, name in [
        ("heavy", "Heavy"),
        ("planned", "Planned"),
        ("tomorrow", "Tomorrow"),
        ("lapsed", "Lapsed"),
        ("justnow", "Just Now"),
    ]:
        _person(db, org_id, pid, name)
    for days in (-1, -5, -10, -20):
        _serve(db, org_id, "heavy", timedelta(days=days))
    for offset in (
        timedelta(days=-3),
        timedelta(days=-40),
        timedelta(hours=2),
        timedelta(days=3),
        timedelta(days=10),
        timedelta(days=17),
    ):
        _serve(db, org_id, "planned", offset)
    for days in (1, 8, 15, 22):
        _serve(db, org_id, "tomorrow", timedelta(days=days))
    _serve(db, org_id, "lapsed", timedelta(days=-45))
    _serve(db, org_id, "justnow", timedelta(hours=-2))
    db.commit()
    return org_id


@pytest.mark.no_mock_auth
class TestLastNDaysWindow:
    """volunteer-stats and burnout-risk count only [now - N days, now]."""

    def test_participation_counts_only_the_past_window(self, client, windowed_org, admin_hdrs):
        body = client.get(
            f"/api/v1/analytics/{windowed_org}/volunteer-stats", headers=admin_hdrs
        ).json()
        # Heavy 4 + Planned 1 + Just Now 1; nothing ahead, nothing before.
        assert body["total_assignments"] == 6
        assert body["active_volunteers"] == 3
        # admin + 5 volunteers
        assert body["total_volunteers"] == 6
        assert body["participation_rate"] == 50.0

    def test_top_volunteers_ignore_future_and_old_assignments(
        self, client, windowed_org, admin_hdrs
    ):
        body = client.get(
            f"/api/v1/analytics/{windowed_org}/volunteer-stats", headers=admin_hdrs
        ).json()
        assert body["top_volunteers"][0] == {"name": "Heavy", "assignments": 4}
        top = {v["name"]: v["assignments"] for v in body["top_volunteers"]}
        assert top == {"Heavy": 4, "Planned": 1, "Just Now": 1}

    def test_days_param_moves_only_the_lower_bound(self, client, windowed_org, admin_hdrs):
        body = client.get(
            f"/api/v1/analytics/{windowed_org}/volunteer-stats?days=7", headers=admin_hdrs
        ).json()
        top = {v["name"]: v["assignments"] for v in body["top_volunteers"]}
        assert top == {"Heavy": 2, "Planned": 1, "Just Now": 1}
        assert body["total_assignments"] == 4

    def test_wide_window_still_excludes_the_future(self, client, windowed_org, admin_hdrs):
        body = client.get(
            f"/api/v1/analytics/{windowed_org}/volunteer-stats?days=365", headers=admin_hdrs
        ).json()
        top = {v["name"]: v["assignments"] for v in body["top_volunteers"]}
        assert top == {"Heavy": 4, "Planned": 2, "Lapsed": 1, "Just Now": 1}
        assert "Tomorrow" not in top

    def test_burnout_counts_only_the_last_30_days(self, client, windowed_org, admin_hdrs):
        body = client.get(
            f"/api/v1/analytics/{windowed_org}/burnout-risk", headers=admin_hdrs
        ).json()
        assert body["at_risk_count"] == 1
        [heavy] = body["at_risk_volunteers"]
        assert heavy["name"] == "Heavy"
        assert heavy["assignments_last_30_days"] == 4

    def test_burnout_low_threshold_never_lists_future_only_volunteers(
        self, client, windowed_org, admin_hdrs
    ):
        body = client.get(
            f"/api/v1/analytics/{windowed_org}/burnout-risk?threshold=1", headers=admin_hdrs
        ).json()
        counts = {v["name"]: v["assignments_last_30_days"] for v in body["at_risk_volunteers"]}
        assert counts == {"Heavy": 4, "Planned": 1, "Just Now": 1}


@pytest.mark.no_mock_auth
class TestScheduleHealthLooksAhead:
    """Upcoming events and coverage stay future-facing, on the same clock."""

    def test_upcoming_events_count_only_the_future(self, client, windowed_org, admin_hdrs):
        body = client.get(
            f"/api/v1/analytics/{windowed_org}/schedule-health", headers=admin_hdrs
        ).json()
        # Planned: +2h, +3d, +10d, +17d; Tomorrow: +1d, +8d, +15d, +22d.
        assert body["upcoming_events"] == 8
        assert body["events_with_assignments"] == 8
        assert body["coverage_rate"] == 100.0

    def test_coverage_counts_unstaffed_future_events(self, client, db, windowed_org, admin_hdrs):
        start = PINNED_NOW + timedelta(days=5)
        db.add(
            Event(
                id="evt_unstaffed",
                org_id=windowed_org,
                type="Sunday Service",
                start_time=start,
                end_time=start + timedelta(hours=2),
            )
        )
        db.commit()
        body = client.get(
            f"/api/v1/analytics/{windowed_org}/schedule-health", headers=admin_hdrs
        ).json()
        assert body["upcoming_events"] == 9
        assert body["events_with_assignments"] == 8
        assert body["coverage_rate"] == 88.9
