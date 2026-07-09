"""Tests for /api/v1/analytics — covers the previously zero-test analytics router.

Sprint 4 PR 4.5d gated all three endpoints behind
`Depends(get_current_admin_user)` + `verify_org_member`. Baseline
smoke tests now authenticate as an admin so they exercise the same
happy paths they always did.
"""

import pytest

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
