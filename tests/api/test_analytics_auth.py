"""Analytics auth-gap tests (Sprint 4 PR 4.5d).

Previously `/analytics/{org_id}/volunteer-stats`, `/schedule-health`, and
`/burnout-risk` accepted `org_id` as a path parameter and returned
volunteer names, emails, and event counts with **no auth check at all**.
Anyone who could reach the API could enumerate any org's roster.

After this PR each endpoint requires an authenticated admin whose own
`org_id` matches the requested one, matching the pattern already used by
`/calendar/org/export` (PR 4.5c).
"""

import pytest

from tests.api.conftest import auth_headers, seed_org, seed_user


def _admin_for(client, org_id: str, suffix: str):
    seed_user(
        client,
        org_id,
        email=f"admin-{suffix}@a.org",
        name="Admin",
        password="AdminPass1!",
    )
    return auth_headers(client, email=f"admin-{suffix}@a.org", password="AdminPass1!")


def _volunteer_for(client, org_id: str, suffix: str):
    seed_user(
        client,
        org_id,
        email=f"vol-{suffix}@a.org",
        name="Vol",
        password="VolPass1!",
        roles=["volunteer"],
    )
    return auth_headers(client, email=f"vol-{suffix}@a.org", password="VolPass1!")


# ---------------------------------------------------------------------------
# volunteer-stats
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestVolunteerStatsAuth:
    def test_no_auth_rejected(self, client, db):
        org_id = "an-vs-noauth"
        seed_org(client, org_id)

        resp = client.get(f"/api/v1/analytics/{org_id}/volunteer-stats")
        assert resp.status_code in (401, 403)

    def test_volunteer_in_same_org_rejected(self, client, db):
        org_id = "an-vs-vol"
        seed_org(client, org_id)
        _admin_for(client, org_id, "vs-vol-a")
        vol_hdrs = _volunteer_for(client, org_id, "vs-vol")

        resp = client.get(f"/api/v1/analytics/{org_id}/volunteer-stats", headers=vol_hdrs)
        assert resp.status_code == 403

    def test_admin_cross_org_rejected(self, client, db):
        seed_org(client, "an-vs-cr-a")
        seed_org(client, "an-vs-cr-b")
        a_hdrs = _admin_for(client, "an-vs-cr-a", "vs-cr-a")
        _admin_for(client, "an-vs-cr-b", "vs-cr-b")

        # Admin of org A asks for org B's volunteer stats.
        resp = client.get(
            "/api/v1/analytics/an-vs-cr-b/volunteer-stats",
            headers=a_hdrs,
        )
        assert resp.status_code == 403

    def test_admin_same_org_ok(self, client, db):
        org_id = "an-vs-ok"
        seed_org(client, org_id)
        a_hdrs = _admin_for(client, org_id, "vs-ok")

        resp = client.get(f"/api/v1/analytics/{org_id}/volunteer-stats", headers=a_hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert body["org_id"] == org_id


# ---------------------------------------------------------------------------
# schedule-health
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestScheduleHealthAuth:
    def test_no_auth_rejected(self, client, db):
        org_id = "an-sh-noauth"
        seed_org(client, org_id)

        resp = client.get(f"/api/v1/analytics/{org_id}/schedule-health")
        assert resp.status_code in (401, 403)

    def test_volunteer_in_same_org_rejected(self, client, db):
        org_id = "an-sh-vol"
        seed_org(client, org_id)
        _admin_for(client, org_id, "sh-vol-a")
        vol_hdrs = _volunteer_for(client, org_id, "sh-vol")

        resp = client.get(f"/api/v1/analytics/{org_id}/schedule-health", headers=vol_hdrs)
        assert resp.status_code == 403

    def test_admin_cross_org_rejected(self, client, db):
        seed_org(client, "an-sh-cr-a")
        seed_org(client, "an-sh-cr-b")
        a_hdrs = _admin_for(client, "an-sh-cr-a", "sh-cr-a")
        _admin_for(client, "an-sh-cr-b", "sh-cr-b")

        resp = client.get("/api/v1/analytics/an-sh-cr-b/schedule-health", headers=a_hdrs)
        assert resp.status_code == 403

    def test_admin_same_org_ok(self, client, db):
        org_id = "an-sh-ok"
        seed_org(client, org_id)
        a_hdrs = _admin_for(client, org_id, "sh-ok")

        resp = client.get(f"/api/v1/analytics/{org_id}/schedule-health", headers=a_hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert body["org_id"] == org_id


# ---------------------------------------------------------------------------
# burnout-risk
# ---------------------------------------------------------------------------


@pytest.mark.no_mock_auth
class TestBurnoutRiskAuth:
    def test_no_auth_rejected(self, client, db):
        org_id = "an-br-noauth"
        seed_org(client, org_id)

        resp = client.get(f"/api/v1/analytics/{org_id}/burnout-risk")
        assert resp.status_code in (401, 403)

    def test_volunteer_in_same_org_rejected(self, client, db):
        """Burnout-risk exposes other volunteers' names + emails — never
        readable by a peer volunteer, even one in the same org."""
        org_id = "an-br-vol"
        seed_org(client, org_id)
        _admin_for(client, org_id, "br-vol-a")
        vol_hdrs = _volunteer_for(client, org_id, "br-vol")

        resp = client.get(f"/api/v1/analytics/{org_id}/burnout-risk", headers=vol_hdrs)
        assert resp.status_code == 403

    def test_admin_cross_org_rejected(self, client, db):
        seed_org(client, "an-br-cr-a")
        seed_org(client, "an-br-cr-b")
        a_hdrs = _admin_for(client, "an-br-cr-a", "br-cr-a")
        _admin_for(client, "an-br-cr-b", "br-cr-b")

        resp = client.get("/api/v1/analytics/an-br-cr-b/burnout-risk", headers=a_hdrs)
        assert resp.status_code == 403

    def test_admin_same_org_ok(self, client, db):
        org_id = "an-br-ok"
        seed_org(client, org_id)
        a_hdrs = _admin_for(client, org_id, "br-ok")

        resp = client.get(f"/api/v1/analytics/{org_id}/burnout-risk", headers=a_hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert body["org_id"] == org_id
