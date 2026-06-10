"""Tests for /api/v1/analytics — covers the previously zero-test analytics router."""

import pytest

from tests.api.conftest import auth_headers, seed_org, seed_user


@pytest.fixture
def org_and_headers(client):
    org = "analytics-test-org"
    seed_org(client, org)
    seed_user(client, org, email="admin@a.org", name="Admin", password="AdminPass1!")
    hdrs = auth_headers(client, email="admin@a.org", password="AdminPass1!")
    return org, hdrs


@pytest.mark.no_mock_auth
class TestVolunteerStats:
    def test_returns_baseline_for_empty_org(self, client, db, org_and_headers):
        org_id, hdrs = org_and_headers
        resp = client.get(f"/api/v1/analytics/{org_id}/volunteer-stats", headers=hdrs)
        assert resp.status_code == 200
        body = resp.json()
        # Whatever the schema, endpoint must succeed and return JSON
        assert isinstance(body, dict)

    def test_404_or_empty_for_unknown_org(self, client, db, org_and_headers):
        _, hdrs = org_and_headers
        # Unknown orgs should not crash; either 404 or empty stats are acceptable.
        resp = client.get("/api/v1/analytics/no-such-org/volunteer-stats", headers=hdrs)
        assert resp.status_code in (200, 403, 404)

    def test_accepts_days_query_param(self, client, db, org_and_headers):
        org_id, hdrs = org_and_headers
        resp = client.get(f"/api/v1/analytics/{org_id}/volunteer-stats?days=7", headers=hdrs)
        assert resp.status_code == 200


@pytest.mark.no_mock_auth
class TestScheduleHealth:
    def test_returns_for_org(self, client, db, org_and_headers):
        org_id, hdrs = org_and_headers
        resp = client.get(f"/api/v1/analytics/{org_id}/schedule-health", headers=hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, dict)


@pytest.mark.no_mock_auth
class TestBurnoutRisk:
    def test_returns_for_org(self, client, db, org_and_headers):
        org_id, hdrs = org_and_headers
        resp = client.get(f"/api/v1/analytics/{org_id}/burnout-risk", headers=hdrs)
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, dict | list)

    def test_no_assignments_means_no_at_risk(self, client, db, org_and_headers):
        """An org with zero events/assignments cannot have burnout risk by definition."""
        org_id, hdrs = org_and_headers
        resp = client.get(f"/api/v1/analytics/{org_id}/burnout-risk", headers=hdrs)
        assert resp.status_code == 200
        body = resp.json()
        # Whether `at_risk_volunteers` is absent or `[]`, the value must be falsy.
        if isinstance(body, dict) and "at_risk_volunteers" in body:
            assert not body["at_risk_volunteers"]
