"""
Organization lifecycle: creation, RBAC, teams, events.

Tests the real-world flow of setting up an organization with proper
role enforcement — first user gets admin, subsequent users are volunteers,
and volunteers can't perform admin actions.
"""

import pytest
from datetime import datetime, timedelta

from tests.api.conftest import (
    seed_org, seed_user, auth_headers, seed_event, seed_team,
)


@pytest.mark.no_mock_auth
class TestOrgLifecycle:

    ORG = "lifecycle-org"
    ADMIN_EMAIL = "admin@lifecycle.com"
    ADMIN_PW = "AdminPass123!"
    VOL_EMAIL = "vol@lifecycle.com"
    VOL_PW = "VolPass123!"

    def test_first_user_becomes_admin(self, client):
        """First user to sign up in an org automatically gets admin role."""
        seed_org(client, self.ORG)
        user = seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin User", self.ADMIN_PW)
        assert "admin" in user["roles"]

    def test_second_user_becomes_volunteer(self, client):
        """Second user can't self-assign admin, defaults to volunteer."""
        seed_org(client, self.ORG)
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin", self.ADMIN_PW)
        vol = seed_user(client, self.ORG, self.VOL_EMAIL, "Volunteer", self.VOL_PW,
                        roles=["admin"])  # Tries to request admin!
        assert "admin" not in vol["roles"]
        assert "volunteer" in vol["roles"]

    def test_duplicate_email_rejected(self, client):
        """Signing up with an existing email returns 409."""
        seed_org(client, self.ORG)
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin", self.ADMIN_PW)
        resp = client.post("/api/auth/signup", json={
            "org_id": self.ORG, "name": "Duplicate",
            "email": self.ADMIN_EMAIL, "password": "AnyPass123!",
        })
        assert resp.status_code == 409

    def test_admin_creates_teams_with_members(self, client):
        """Admin can create teams and add volunteers as members."""
        seed_org(client, self.ORG)
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin", self.ADMIN_PW)
        vol = seed_user(client, self.ORG, self.VOL_EMAIL, "Sarah", self.VOL_PW)
        hdrs = auth_headers(client, self.ADMIN_EMAIL, self.ADMIN_PW)

        team = seed_team(client, hdrs, self.ORG, "team-ushers", "Ushers",
                        member_ids=[vol["person_id"]])
        assert team["name"] == "Ushers"

        # Verify team in list
        resp = client.get(f"/api/teams/?org_id={self.ORG}", headers=hdrs)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_admin_creates_events(self, client):
        """Admin can create events with role requirements."""
        seed_org(client, self.ORG)
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin", self.ADMIN_PW)
        hdrs = auth_headers(client, self.ADMIN_EMAIL, self.ADMIN_PW)

        event = seed_event(client, hdrs, self.ORG, "evt-sunday",
                          event_type="Sunday Service",
                          role_counts={"volunteer": 3, "leader": 1})
        assert event["org_id"] == self.ORG

    def test_volunteer_cannot_create_events(self, client):
        """Volunteer gets 403 when trying to create events."""
        seed_org(client, self.ORG)
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin", self.ADMIN_PW)
        seed_user(client, self.ORG, self.VOL_EMAIL, "Vol", self.VOL_PW)
        vol_hdrs = auth_headers(client, self.VOL_EMAIL, self.VOL_PW)

        start = (datetime.now() + timedelta(days=7)).isoformat()
        end = (datetime.now() + timedelta(days=7, hours=2)).isoformat()
        resp = client.post("/api/events/", json={
            "id": "evt-forbidden", "org_id": self.ORG, "type": "Test",
            "start_time": start, "end_time": end,
        }, headers=vol_hdrs)
        assert resp.status_code == 403

    def test_volunteer_cannot_create_teams(self, client):
        """Volunteer gets 403 when trying to create teams."""
        seed_org(client, self.ORG)
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin", self.ADMIN_PW)
        seed_user(client, self.ORG, self.VOL_EMAIL, "Vol", self.VOL_PW)
        vol_hdrs = auth_headers(client, self.VOL_EMAIL, self.VOL_PW)

        resp = client.post("/api/teams/", json={
            "id": "team-forbidden", "org_id": self.ORG, "name": "Forbidden",
        }, headers=vol_hdrs)
        assert resp.status_code == 403

    def test_volunteer_can_view_own_profile(self, client):
        """Volunteer can read their own profile via /people/me."""
        seed_org(client, self.ORG)
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin", self.ADMIN_PW)
        seed_user(client, self.ORG, self.VOL_EMAIL, "Sarah", self.VOL_PW)
        vol_hdrs = auth_headers(client, self.VOL_EMAIL, self.VOL_PW)

        resp = client.get("/api/people/me", headers=vol_hdrs)
        assert resp.status_code == 200
        assert resp.json()["email"] == self.VOL_EMAIL

    def test_volunteer_can_list_org_people(self, client):
        """Volunteer can list people in their own org."""
        seed_org(client, self.ORG)
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Admin", self.ADMIN_PW)
        seed_user(client, self.ORG, self.VOL_EMAIL, "Sarah", self.VOL_PW)
        vol_hdrs = auth_headers(client, self.VOL_EMAIL, self.VOL_PW)

        resp = client.get(f"/api/people/?org_id={self.ORG}", headers=vol_hdrs)
        assert resp.status_code == 200
        assert resp.json()["total"] == 2
