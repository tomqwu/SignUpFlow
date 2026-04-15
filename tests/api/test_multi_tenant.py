"""
Multi-tenancy isolation tests.

Verifies that organizations are fully isolated — users in one org
cannot see, modify, or interact with another org's data.
"""

import pytest
from datetime import datetime, timedelta

from tests.api.conftest import (
    seed_org, seed_user, auth_headers, seed_event, seed_team,
)


@pytest.mark.no_mock_auth
class TestMultiTenantIsolation:

    ORG1 = "alpha-church"
    ORG2 = "beta-church"

    def _setup_two_orgs(self, client):
        """Helper: create two orgs with admins, return their headers."""
        seed_org(client, self.ORG1, name="Alpha Church")
        seed_org(client, self.ORG2, name="Beta Church")
        seed_user(client, self.ORG1, "admin@alpha.com", "Alpha Admin", "Pass123!")
        seed_user(client, self.ORG2, "admin@beta.com", "Beta Admin", "Pass123!")
        hdrs1 = auth_headers(client, "admin@alpha.com", "Pass123!")
        hdrs2 = auth_headers(client, "admin@beta.com", "Pass123!")
        return hdrs1, hdrs2

    def test_people_isolated_between_orgs(self, client):
        """Admin of org1 can only see org1's people."""
        hdrs1, hdrs2 = self._setup_two_orgs(client)

        # Each org lists its own people
        resp1 = client.get(f"/api/people/?org_id={self.ORG1}", headers=hdrs1)
        resp2 = client.get(f"/api/people/?org_id={self.ORG2}", headers=hdrs2)
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert all(p["org_id"] == self.ORG1 for p in resp1.json()["people"])
        assert all(p["org_id"] == self.ORG2 for p in resp2.json()["people"])

    def test_cross_org_people_access_denied(self, client):
        """Admin of org1 gets 403 trying to list org2's people."""
        hdrs1, _ = self._setup_two_orgs(client)
        resp = client.get(f"/api/people/?org_id={self.ORG2}", headers=hdrs1)
        assert resp.status_code == 403

    def test_cross_org_team_access_denied(self, client):
        """Admin of org1 gets 403 trying to list org2's teams."""
        hdrs1, hdrs2 = self._setup_two_orgs(client)
        seed_team(client, hdrs2, self.ORG2, "beta-team", "Beta Ushers")

        resp = client.get(f"/api/teams/?org_id={self.ORG2}", headers=hdrs1)
        assert resp.status_code == 403

    def test_cross_org_event_creation_denied(self, client):
        """Admin of org1 can't create events in org2."""
        hdrs1, _ = self._setup_two_orgs(client)

        start = (datetime.now() + timedelta(days=7)).isoformat()
        end = (datetime.now() + timedelta(days=7, hours=2)).isoformat()
        resp = client.post("/api/events/", json={
            "id": "evt-cross", "org_id": self.ORG2, "type": "Test",
            "start_time": start, "end_time": end,
        }, headers=hdrs1)
        assert resp.status_code == 403

    def test_cross_org_solver_denied(self, client):
        """Admin of org1 can't run solver for org2."""
        hdrs1, _ = self._setup_two_orgs(client)
        resp = client.post("/api/solver/solve", json={
            "org_id": self.ORG2,
            "from_date": "2026-05-01", "to_date": "2026-05-31",
            "mode": "strict", "change_min": False,
        }, headers=hdrs1)
        assert resp.status_code == 403

    def test_each_org_has_independent_events(self, client):
        """Events in org1 don't appear in org2's event list."""
        hdrs1, hdrs2 = self._setup_two_orgs(client)

        seed_event(client, hdrs1, self.ORG1, "evt-alpha-only")
        seed_event(client, hdrs2, self.ORG2, "evt-beta-only")

        resp1 = client.get(f"/api/events/?org_id={self.ORG1}")
        resp2 = client.get(f"/api/events/?org_id={self.ORG2}")
        assert resp1.status_code == 200
        assert resp2.status_code == 200

        ids1 = [e["id"] for e in resp1.json()["events"]]
        ids2 = [e["id"] for e in resp2.json()["events"]]
        assert "evt-alpha-only" in ids1
        assert "evt-alpha-only" not in ids2
        assert "evt-beta-only" in ids2
        assert "evt-beta-only" not in ids1

    def test_unauthenticated_access_denied(self, client):
        """API endpoints that require auth reject unauthenticated requests."""
        seed_org(client, self.ORG1)

        resp = client.get(f"/api/people/?org_id={self.ORG1}")
        assert resp.status_code in (401, 403)

        resp = client.post("/api/events/", json={
            "id": "evt-noauth", "org_id": self.ORG1, "type": "Test",
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        })
        assert resp.status_code in (401, 403)
