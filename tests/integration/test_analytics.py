#!/usr/bin/env python3
"""Integration tests: analytics router (Sprint 4 PR 4.6b).

Drives the /api/v1/analytics endpoints over real HTTP against the
session-scoped uvicorn api_server:
- GET /analytics/{org_id}/volunteer-stats   - admin only
- GET /analytics/{org_id}/schedule-health   - admin only
- GET /analytics/{org_id}/burnout-risk      - admin only (exposes emails)

All three endpoints are admin-only within their `org_id`, so coverage
locks in:
- 401/403 unauthenticated
- 403 when a volunteer calls
- 403 when an admin of a different org calls (verify_org_member)
- Real derived metrics (participation_rate, coverage_rate, at_risk_count)
  respond to actual DB state, not just synthetic zeros
"""

import random
import time
from datetime import UTC, datetime, timedelta

import httpx
import pytest


def _unique(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(10000, 99999)}"


def _future(days: int, hours: int = 0) -> str:
    dt = datetime.now(UTC) + timedelta(days=days, hours=hours)
    return dt.isoformat()


def _past(days: int, hours: int = 0) -> str:
    dt = datetime.now(UTC) - timedelta(days=days, hours=hours)
    return dt.isoformat()


@pytest.fixture
def analytics_org(api_server, api_base):
    """Two independent orgs so cross-org assertions have a real second org.

    org1 gets an admin, two volunteers, and some assignments (one recent,
    one past) so the derived metrics are non-trivial. org2 gets an admin
    only — enough to test the cross-org 403.
    """
    marker = _unique("analytics_org")
    org1_id = f"{marker}_a"
    org2_id = f"{marker}_b"

    bootstrap = httpx.Client()

    for oid in (org1_id, org2_id):
        resp = bootstrap.post(
            f"{api_base}/organizations/",
            json={"id": oid, "name": f"Analytics Setup {oid}", "region": "US", "config": {}},
        )
        assert resp.status_code == 201, resp.text

    def _signup(org_id: str, name: str, email: str, roles: list[str] | None = None) -> dict:
        body = {
            "org_id": org_id,
            "name": name,
            "email": email,
            "password": "TestPass123!",
        }
        if roles is not None:
            body["roles"] = roles
        r = bootstrap.post(f"{api_base}/auth/signup", json=body)
        assert r.status_code == 201, r.text
        return r.json()

    admin1 = _signup(org1_id, "Org1 Admin", f"admin1_{marker}@t.com")
    admin2 = _signup(org2_id, "Org2 Admin", f"admin2_{marker}@t.com")
    vol1 = _signup(org1_id, "Vol A", f"vola_{marker}@t.com", roles=["volunteer"])
    vol2 = _signup(org1_id, "Vol B", f"volb_{marker}@t.com", roles=["volunteer"])
    bootstrap.close()

    def _client(token: str) -> httpx.Client:
        c = httpx.Client()
        c.headers["Authorization"] = f"Bearer {token}"
        return c

    admin1_c = _client(admin1["token"])
    admin2_c = _client(admin2["token"])
    vol1_c = _client(vol1["token"])

    # Seed some data in org1 so metrics are non-zero.
    # Recent event (within last 30 days for volunteer-stats window) with two
    # assignments; upcoming event for schedule-health coverage.
    recent_event_id = _unique("evt_recent")
    upcoming_event_id = _unique("evt_upcoming")

    # Recent event with start_time in the past 3 days.
    recent_start = _past(3)
    recent_end = _past(3, hours=-2)  # 2h after start (still in the past)
    r = admin1_c.post(
        f"{api_base}/events/",
        json={
            "id": recent_event_id,
            "org_id": org1_id,
            "type": "meeting",
            "start_time": recent_start,
            "end_time": recent_end,
        },
    )
    assert r.status_code == 201, r.text

    # Assign both volunteers so total_assignments = 2 and active_volunteers = 2.
    for v in (vol1, vol2):
        r = admin1_c.post(
            f"{api_base}/events/{recent_event_id}/assignments",
            json={"person_id": v["person_id"], "action": "assign"},
        )
        assert r.status_code == 200, r.text

    # Upcoming event (unassigned) so coverage_rate < 100.
    r = admin1_c.post(
        f"{api_base}/events/",
        json={
            "id": upcoming_event_id,
            "org_id": org1_id,
            "type": "meeting",
            "start_time": _future(10),
            "end_time": _future(10, hours=2),
        },
    )
    assert r.status_code == 201, r.text

    yield {
        "marker": marker,
        "org1_id": org1_id,
        "org2_id": org2_id,
        "admin1_client": admin1_c,
        "admin2_client": admin2_c,
        "vol1_client": vol1_c,
        "vol1_id": vol1["person_id"],
        "vol2_id": vol2["person_id"],
        "api_base": api_base,
    }

    admin1_c.close()
    admin2_c.close()
    vol1_c.close()


class TestVolunteerStats:
    """GET /analytics/{org_id}/volunteer-stats — admin-only."""

    def test_admin_gets_participation(self, analytics_org):
        data = analytics_org
        resp = data["admin1_client"].get(
            f"{data['api_base']}/analytics/{data['org1_id']}/volunteer-stats"
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["org_id"] == data["org1_id"]
        assert body["period_days"] == 30
        assert body["total_volunteers"] >= 2
        assert body["active_volunteers"] >= 2
        assert body["total_assignments"] >= 2
        assert body["participation_rate"] > 0
        # Top volunteers should include both seeded vols; each with count >= 1.
        top_names = {v["name"] for v in body["top_volunteers"]}
        assert "Vol A" in top_names
        assert "Vol B" in top_names

    def test_days_query_param_narrows_window(self, analytics_org):
        data = analytics_org
        # days=1 is narrower than the 3-day-old assignment we seeded.
        resp = data["admin1_client"].get(
            f"{data['api_base']}/analytics/{data['org1_id']}/volunteer-stats",
            params={"days": 1},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["period_days"] == 1
        assert body["total_assignments"] == 0
        assert body["active_volunteers"] == 0

    def test_volunteer_forbidden(self, analytics_org):
        data = analytics_org
        resp = data["vol1_client"].get(
            f"{data['api_base']}/analytics/{data['org1_id']}/volunteer-stats"
        )
        assert resp.status_code == 403

    def test_cross_org_admin_forbidden(self, analytics_org):
        data = analytics_org
        resp = data["admin2_client"].get(
            f"{data['api_base']}/analytics/{data['org1_id']}/volunteer-stats"
        )
        assert resp.status_code == 403

    def test_unauthenticated(self, analytics_org):
        data = analytics_org
        with httpx.Client() as anon:
            resp = anon.get(f"{data['api_base']}/analytics/{data['org1_id']}/volunteer-stats")
        assert resp.status_code in (401, 403)


class TestScheduleHealth:
    """GET /analytics/{org_id}/schedule-health — admin-only."""

    def test_admin_gets_health(self, analytics_org):
        data = analytics_org
        resp = data["admin1_client"].get(
            f"{data['api_base']}/analytics/{data['org1_id']}/schedule-health"
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["org_id"] == data["org1_id"]
        # Upcoming events in this org: the unassigned one we created.
        assert body["upcoming_events"] >= 1
        # It has no assignments, so events_with_assignments could be 0 unless
        # other tests seeded an upcoming assigned event; either way the ratio
        # must land in [0, 100].
        assert 0 <= body["coverage_rate"] <= 100
        # No solutions were seeded, so latest_solution should be None.
        assert body["latest_solution"] is None

    def test_volunteer_forbidden(self, analytics_org):
        data = analytics_org
        resp = data["vol1_client"].get(
            f"{data['api_base']}/analytics/{data['org1_id']}/schedule-health"
        )
        assert resp.status_code == 403

    def test_cross_org_admin_forbidden(self, analytics_org):
        data = analytics_org
        resp = data["admin2_client"].get(
            f"{data['api_base']}/analytics/{data['org1_id']}/schedule-health"
        )
        assert resp.status_code == 403


class TestBurnoutRisk:
    """GET /analytics/{org_id}/burnout-risk — admin-only.

    The endpoint returns other volunteers' names + emails, so the peer-
    volunteer path must be forbidden.
    """

    def test_default_threshold_no_burnout(self, analytics_org):
        data = analytics_org
        # Default threshold is 4/month; our seeded volunteers have 1
        # assignment each, so nobody is at risk.
        resp = data["admin1_client"].get(
            f"{data['api_base']}/analytics/{data['org1_id']}/burnout-risk"
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["org_id"] == data["org1_id"]
        assert body["threshold"] == 4
        assert body["at_risk_count"] == 0
        assert body["at_risk_volunteers"] == []

    def test_low_threshold_flags_volunteers(self, analytics_org):
        data = analytics_org
        # threshold=1 will match anyone with >=1 assignment in last 30d,
        # so both seeded volunteers surface.
        resp = data["admin1_client"].get(
            f"{data['api_base']}/analytics/{data['org1_id']}/burnout-risk",
            params={"threshold": 1},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["threshold"] == 1
        assert body["at_risk_count"] >= 2
        # Assert the response includes the actual identifying fields (this
        # is why the endpoint is admin-only).
        names = {v["name"] for v in body["at_risk_volunteers"]}
        emails = {v["email"] for v in body["at_risk_volunteers"]}
        assert "Vol A" in names
        assert "Vol B" in names
        assert any("vola_" in e for e in emails)

    def test_volunteer_forbidden(self, analytics_org):
        data = analytics_org
        resp = data["vol1_client"].get(
            f"{data['api_base']}/analytics/{data['org1_id']}/burnout-risk"
        )
        assert resp.status_code == 403

    def test_cross_org_admin_forbidden(self, analytics_org):
        data = analytics_org
        resp = data["admin2_client"].get(
            f"{data['api_base']}/analytics/{data['org1_id']}/burnout-risk"
        )
        assert resp.status_code == 403
