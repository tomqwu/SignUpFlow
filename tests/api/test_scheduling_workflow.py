"""
Core scheduling workflow: org setup -> volunteers -> availability -> solver.

Tests the complete real-world lifecycle that a church or non-profit admin
would go through to schedule volunteers for events.
"""

import pytest
from datetime import datetime, timedelta

from tests.api.conftest import (
    seed_org, seed_user, auth_headers, seed_event,
    seed_invitation, accept_invitation, add_timeoff,
)


@pytest.mark.no_mock_auth
class TestSchedulingWorkflow:
    """Full scheduling lifecycle from org creation through solver execution."""

    ORG = "grace-church"
    ADMIN_EMAIL = "pastor@grace.church"
    ADMIN_PW = "AdminPass123!"

    def test_full_scheduling_lifecycle(self, client):
        """
        Real-world scenario: A church admin sets up Sunday services,
        invites volunteers, they set availability, then admin runs solver.
        """
        # -- Org + admin setup --
        seed_org(client, self.ORG, name="Grace Church")
        admin = seed_user(client, self.ORG, self.ADMIN_EMAIL, "Pastor Mike", self.ADMIN_PW)
        assert "admin" in admin["roles"]
        hdrs = auth_headers(client, self.ADMIN_EMAIL, self.ADMIN_PW)

        # -- Create 3 weekly events with role requirements --
        base = datetime.now() + timedelta(days=14)
        event_ids = []
        for i in range(3):
            eid = f"sunday-{i}"
            seed_event(client, hdrs, self.ORG, eid,
                       event_type="Sunday Service",
                       days_from_now=14 + (i * 7),
                       role_counts={"volunteer": 2})
            event_ids.append(eid)

        # Verify events created
        resp = client.get(f"/api/events/?org_id={self.ORG}")
        assert resp.status_code == 200
        assert resp.json()["total"] == 3

        # -- Invite 5 volunteers --
        vol_emails = [f"vol{i}@grace.church" for i in range(5)]
        vol_pw = "VolPass123!"
        tokens = []
        for i, email in enumerate(vol_emails):
            inv = seed_invitation(client, hdrs, self.ORG, email, f"Volunteer {i}")
            tokens.append(inv["token"])

        # -- Volunteers accept invitations and log in --
        volunteers = []
        for i, token in enumerate(tokens):
            accepted = accept_invitation(client, token, password=vol_pw)
            assert accepted["org_id"] == self.ORG
            # Must login to get JWT (invitation token is not a JWT)
            vol_hdrs = auth_headers(client, vol_emails[i], vol_pw)
            volunteers.append({
                "person_id": accepted["person_id"],
                "email": vol_emails[i],
                "headers": vol_hdrs,
            })

        # Verify all people exist (1 admin + 5 volunteers)
        resp = client.get(f"/api/people/?org_id={self.ORG}", headers=hdrs)
        assert resp.status_code == 200
        assert resp.json()["total"] == 6

        # -- 2 volunteers block the first event's date --
        first_event_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        for vol in volunteers[:2]:
            add_timeoff(client, vol["person_id"], first_event_date, first_event_date,
                        reason="Family commitment")

        # Verify time-off recorded
        for vol in volunteers[:2]:
            resp = client.get(f"/api/availability/{vol['person_id']}/timeoff")
            assert resp.status_code == 200
            assert resp.json()["total"] == 1

        # -- Run solver --
        from_date = (datetime.now() + timedelta(days=13)).strftime("%Y-%m-%d")
        to_date = (datetime.now() + timedelta(days=40)).strftime("%Y-%m-%d")
        resp = client.post("/api/solver/solve", json={
            "org_id": self.ORG,
            "from_date": from_date,
            "to_date": to_date,
            "mode": "relaxed",
            "change_min": False,
        }, headers=hdrs)
        assert resp.status_code == 200, f"Solver failed: {resp.status_code} {resp.text}"

        solution = resp.json()
        assert solution["solution_id"] is not None
        assert solution["assignment_count"] > 0
        assert solution["metrics"]["health_score"] >= 0

        # -- Verify solution in solutions list --
        resp = client.get(f"/api/solutions/?org_id={self.ORG}", headers=hdrs)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_solver_rejects_empty_date_range(self, client):
        """Solver returns 400 when no events exist in the date range."""
        seed_org(client, self.ORG, name="Grace Church")
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Pastor", self.ADMIN_PW)
        hdrs = auth_headers(client, self.ADMIN_EMAIL, self.ADMIN_PW)

        # Event is 14 days out, but we query a range that doesn't include it
        seed_event(client, hdrs, self.ORG, "evt-far", days_from_now=60)

        resp = client.post("/api/solver/solve", json={
            "org_id": self.ORG,
            "from_date": "2026-01-01",
            "to_date": "2026-01-31",
            "mode": "strict",
            "change_min": False,
        }, headers=hdrs)
        assert resp.status_code == 400

    def test_manual_assignment(self, client):
        """Admin can manually assign a volunteer to an event."""
        seed_org(client, self.ORG, name="Grace Church")
        admin = seed_user(client, self.ORG, self.ADMIN_EMAIL, "Pastor", self.ADMIN_PW)
        vol = seed_user(client, self.ORG, "vol@grace.church", "Sarah", "VolPass123!")
        hdrs = auth_headers(client, self.ADMIN_EMAIL, self.ADMIN_PW)

        event = seed_event(client, hdrs, self.ORG, "evt-manual",
                          role_counts={"volunteer": 2})

        # Assign volunteer to event
        resp = client.post(f"/api/events/{event['id']}/assignments", json={
            "person_id": vol["person_id"],
            "action": "assign",
            "role": "volunteer",
        }, headers=hdrs)
        assert resp.status_code == 200

        # Verify assignment shows up
        resp = client.get(f"/api/events/assignments/all?org_id={self.ORG}")
        assert resp.status_code == 200
        assignments = resp.json()["assignments"]
        assert any(a["person_id"] == vol["person_id"] for a in assignments)

    def test_unassign_volunteer(self, client):
        """Admin can unassign a volunteer from an event."""
        seed_org(client, self.ORG, name="Grace Church")
        seed_user(client, self.ORG, self.ADMIN_EMAIL, "Pastor", self.ADMIN_PW)
        vol = seed_user(client, self.ORG, "vol@grace.church", "Sarah", "VolPass123!")
        hdrs = auth_headers(client, self.ADMIN_EMAIL, self.ADMIN_PW)

        event = seed_event(client, hdrs, self.ORG, "evt-unassign",
                          role_counts={"volunteer": 2})

        # Assign then unassign
        client.post(f"/api/events/{event['id']}/assignments", json={
            "person_id": vol["person_id"], "action": "assign", "role": "volunteer",
        }, headers=hdrs)

        resp = client.post(f"/api/events/{event['id']}/assignments", json={
            "person_id": vol["person_id"], "action": "unassign",
        }, headers=hdrs)
        assert resp.status_code == 200
