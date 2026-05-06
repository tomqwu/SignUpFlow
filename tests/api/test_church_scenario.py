"""
Scenario: Grace Community Church — weekly ministry scheduling.

Cast:
  Pastor Mike  — admin, oversees everything
  Sarah Chen   — serves on worship team (keyboard) AND teaches Sunday School
  David Kim    — worship team (vocals) and sound tech
  Maria Lopez  — Sunday School teacher and children's ministry
  James Brown  — usher and greeter
  Emily Davis  — worship team (guitar) and youth group leader

Events (weekly recurring pattern):
  Sunday Worship Service   — needs: worship_leader x1, musician x2, sound_tech x1, usher x2
  Sunday School (9am)      — needs: teacher x2, assistant x1
  Wednesday Youth Group    — needs: youth_leader x1, volunteer x2
  Monthly Prayer Meeting   — needs: worship_leader x1, volunteer x3

Real-world tensions:
  - Sarah teaches Sunday School AND plays keyboard → can she do both on the same Sunday?
  - David does sound AND vocals → solver must pick one per service
  - Maria is on vacation for 2 weeks in summer
  - James only available on Sundays (blocks Wednesday)
"""

from datetime import datetime, timedelta

import pytest

from tests.api.conftest import (
    accept_invitation,
    add_timeoff,
    auth_headers,
    seed_event,
    seed_invitation,
    seed_org,
    seed_team,
    seed_user,
)


@pytest.mark.no_mock_auth
class TestChurchScenario:
    """Grace Community Church: real-world ministry scheduling."""

    ORG = "grace-community"
    PASTOR_EMAIL = "pastor.mike@grace.org"
    PASTOR_PW = "PastorPass123!"

    MEMBERS = [
        {"email": "sarah.chen@grace.org", "name": "Sarah Chen", "roles": ["musician", "teacher"]},
        {"email": "david.kim@grace.org", "name": "David Kim", "roles": ["musician", "sound_tech"]},
        {
            "email": "maria.lopez@grace.org",
            "name": "Maria Lopez",
            "roles": ["teacher", "volunteer"],
        },
        {"email": "james.brown@grace.org", "name": "James Brown", "roles": ["usher", "volunteer"]},
        {
            "email": "emily.davis@grace.org",
            "name": "Emily Davis",
            "roles": ["musician", "youth_leader"],
        },
    ]

    VOL_PW = "Member123!"

    def _setup_church(self, client):
        """Set up the church org with pastor and all members."""
        seed_org(client, self.ORG, name="Grace Community Church")
        seed_user(client, self.ORG, self.PASTOR_EMAIL, "Pastor Mike", self.PASTOR_PW)
        hdrs = auth_headers(client, self.PASTOR_EMAIL, self.PASTOR_PW)

        members = {}
        for m in self.MEMBERS:
            inv = seed_invitation(client, hdrs, self.ORG, m["email"], m["name"], roles=m["roles"])
            accepted = accept_invitation(client, inv["token"], password=self.VOL_PW)
            members[m["email"]] = {
                "person_id": accepted["person_id"],
                "name": m["name"],
                "roles": m["roles"],
            }

        return hdrs, members

    # ------------------------------------------------------------------
    # Test: Full church setup and member registration
    # ------------------------------------------------------------------

    def test_church_setup_and_member_roles(self, client):
        """Pastor sets up church, invites members with ministry roles."""
        hdrs, members = self._setup_church(client)

        # Verify all 6 people in org (pastor + 5 members)
        resp = client.get(f"/api/v1/people/?org_id={self.ORG}", headers=hdrs)
        assert resp.status_code == 200
        assert resp.json()["total"] == 6

        # Verify Sarah has dual roles
        members["sarah.chen@grace.org"]
        sarah_hdrs = auth_headers(client, "sarah.chen@grace.org", self.VOL_PW)
        resp = client.get("/api/v1/people/me", headers=sarah_hdrs)
        assert resp.status_code == 200
        profile = resp.json()
        assert "musician" in profile["roles"]
        assert "teacher" in profile["roles"]

    # ------------------------------------------------------------------
    # Test: Ministry teams
    # ------------------------------------------------------------------

    def test_ministry_teams(self, client):
        """Pastor creates worship team and teaching team."""
        hdrs, members = self._setup_church(client)

        # Create worship team: Sarah, David, Emily
        worship_ids = [
            members["sarah.chen@grace.org"]["person_id"],
            members["david.kim@grace.org"]["person_id"],
            members["emily.davis@grace.org"]["person_id"],
        ]
        worship = seed_team(
            client, hdrs, self.ORG, "worship-team", "Worship Team", member_ids=worship_ids
        )
        assert worship["name"] == "Worship Team"

        # Create teaching team: Sarah, Maria
        teach_ids = [
            members["sarah.chen@grace.org"]["person_id"],
            members["maria.lopez@grace.org"]["person_id"],
        ]
        teaching = seed_team(
            client, hdrs, self.ORG, "teaching-team", "Teaching Team", member_ids=teach_ids
        )
        assert teaching["name"] == "Teaching Team"

        # Sarah is on BOTH teams
        resp = client.get(f"/api/v1/teams/?org_id={self.ORG}", headers=hdrs)
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

    # ------------------------------------------------------------------
    # Test: Sunday event setup with role requirements
    # ------------------------------------------------------------------

    def test_sunday_events_with_roles(self, client):
        """Pastor creates Sunday Worship and Sunday School with specific role needs."""
        hdrs, members = self._setup_church(client)

        # Sunday Worship: 2 musicians, 1 sound_tech, 2 ushers
        worship = seed_event(
            client,
            hdrs,
            self.ORG,
            "sunday-worship",
            event_type="Sunday Worship",
            days_from_now=14,
            role_counts={"musician": 2, "sound_tech": 1, "usher": 2},
        )
        assert worship["extra_data"]["role_counts"]["musician"] == 2

        # Sunday School (same day, earlier): 2 teachers, 1 volunteer
        school = seed_event(
            client,
            hdrs,
            self.ORG,
            "sunday-school",
            event_type="Sunday School",
            days_from_now=14,
            duration_hours=1,
            role_counts={"teacher": 2, "volunteer": 1},
        )
        assert school["extra_data"]["role_counts"]["teacher"] == 2

        # Wednesday Youth Group: 1 youth_leader, 2 volunteers
        seed_event(
            client,
            hdrs,
            self.ORG,
            "wed-youth",
            event_type="Youth Group",
            days_from_now=17,
            role_counts={"youth_leader": 1, "volunteer": 2},
        )

        resp = client.get(f"/api/v1/events/?org_id={self.ORG}")
        assert resp.status_code == 200
        assert resp.json()["total"] == 3

    # ------------------------------------------------------------------
    # Test: Vacation / time-off
    # ------------------------------------------------------------------

    def test_member_vacation(self, client):
        """Maria blocks 2 weeks for family vacation; James blocks Wednesdays."""
        hdrs, members = self._setup_church(client)

        maria_id = members["maria.lopez@grace.org"]["person_id"]
        james_id = members["james.brown@grace.org"]["person_id"]

        # Maria: 2-week vacation
        vacation_start = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        vacation_end = (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d")
        add_timeoff(
            client, maria_id, vacation_start, vacation_end, reason="Family vacation in Mexico"
        )

        # James: block the Wednesday (youth group day)
        wed_date = (datetime.now() + timedelta(days=17)).strftime("%Y-%m-%d")
        add_timeoff(client, james_id, wed_date, wed_date, reason="Work commitment")

        # Verify time-off recorded
        resp = client.get(f"/api/v1/availability/{maria_id}/timeoff")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
        assert resp.json()["timeoff"][0]["reason"] == "Family vacation in Mexico"

        resp = client.get(f"/api/v1/availability/{james_id}/timeoff")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    # ------------------------------------------------------------------
    # Test: Solver generates a schedule
    # ------------------------------------------------------------------

    def test_solver_schedules_sunday_services(self, client):
        """
        Pastor runs solver for a month of Sundays.
        Verifies: solution created, assignments generated, fairness tracked.
        """
        hdrs, members = self._setup_church(client)

        # Create 4 weeks of Sunday Worship
        for week in range(4):
            seed_event(
                client,
                hdrs,
                self.ORG,
                f"worship-wk{week}",
                event_type="Sunday Worship",
                days_from_now=14 + (week * 7),
                role_counts={"musician": 2, "sound_tech": 1, "usher": 1},
            )

        # Run solver
        from_date = (datetime.now() + timedelta(days=13)).strftime("%Y-%m-%d")
        to_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
        resp = client.post(
            "/api/v1/solver/solve",
            json={
                "org_id": self.ORG,
                "from_date": from_date,
                "to_date": to_date,
                "mode": "relaxed",
                "change_min": False,
            },
            headers=hdrs,
        )
        assert resp.status_code == 200, f"Solver failed: {resp.text}"

        solution = resp.json()
        assert solution["solution_id"] is not None
        assert solution["assignment_count"] > 0

        # Verify fairness metrics exist
        assert "fairness" in solution["metrics"]
        fairness = solution["metrics"]["fairness"]
        assert "stdev" in fairness
        assert "per_person_counts" in fairness

        # Verify assignments via API
        resp = client.get(f"/api/v1/events/assignments/all?org_id={self.ORG}")
        assert resp.status_code == 200
        assignments = resp.json()["assignments"]
        assert len(assignments) > 0

        # Each event should have at least some assignments
        assigned_events = {a["event_id"] for a in assignments}
        for week in range(4):
            assert f"worship-wk{week}" in assigned_events

    # ------------------------------------------------------------------
    # Test: Manual assignment by pastor
    # ------------------------------------------------------------------

    def test_pastor_manually_assigns_worship_leader(self, client):
        """Pastor manually assigns Sarah as worship leader for a specific Sunday."""
        hdrs, members = self._setup_church(client)

        event = seed_event(
            client,
            hdrs,
            self.ORG,
            "special-sunday",
            event_type="Easter Service",
            days_from_now=21,
            role_counts={"musician": 3, "sound_tech": 1, "usher": 2},
        )

        sarah_id = members["sarah.chen@grace.org"]["person_id"]

        # Pastor assigns Sarah as musician
        resp = client.post(
            f"/api/v1/events/{event['id']}/assignments",
            json={
                "person_id": sarah_id,
                "action": "assign",
                "role": "musician",
            },
            headers=hdrs,
        )
        assert resp.status_code == 200

        # Verify assignment
        resp = client.get(f"/api/v1/events/assignments/all?org_id={self.ORG}")
        assert resp.status_code == 200
        assignments = resp.json()["assignments"]
        sarah_assigned = [
            a
            for a in assignments
            if a["person_id"] == sarah_id and a["event_id"] == "special-sunday"
        ]
        assert len(sarah_assigned) == 1

    # ------------------------------------------------------------------
    # Test: Member views their own schedule
    # ------------------------------------------------------------------

    def test_member_views_own_assignments(self, client):
        """After solver runs, Sarah can see her assignments."""
        hdrs, members = self._setup_church(client)

        # Create events and run solver
        for week in range(2):
            seed_event(
                client,
                hdrs,
                self.ORG,
                f"svc-{week}",
                event_type="Sunday Worship",
                days_from_now=14 + (week * 7),
                role_counts={"musician": 2, "sound_tech": 1},
            )

        from_date = (datetime.now() + timedelta(days=13)).strftime("%Y-%m-%d")
        to_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        client.post(
            "/api/v1/solver/solve",
            json={
                "org_id": self.ORG,
                "from_date": from_date,
                "to_date": to_date,
                "mode": "relaxed",
                "change_min": False,
            },
            headers=hdrs,
        )

        # Sarah logs in and checks assignments
        sarah_hdrs = auth_headers(client, "sarah.chen@grace.org", self.VOL_PW)
        resp = client.get("/api/v1/people/me", headers=sarah_hdrs)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Sarah Chen"

        # Assignments list is org-wide (Sarah can see it)
        resp = client.get(f"/api/v1/events/assignments/all?org_id={self.ORG}")
        assert resp.status_code == 200

    # ------------------------------------------------------------------
    # Test: Invitation workflow for new member
    # ------------------------------------------------------------------

    def test_new_member_joins_via_invitation(self, client):
        """A new person joins after receiving an invitation from the pastor."""
        hdrs, _ = self._setup_church(client)

        # Pastor invites a new member
        inv = seed_invitation(
            client,
            hdrs,
            self.ORG,
            "rachel.wong@gmail.com",
            "Rachel Wong",
            roles=["volunteer", "teacher"],
        )

        # Verify invitation is pending
        resp = client.get(f"/api/v1/invitations?org_id={self.ORG}", headers=hdrs)
        assert resp.status_code == 200
        pending = [i for i in resp.json()["items"] if i["email"] == "rachel.wong@gmail.com"]
        assert len(pending) == 1
        assert pending[0]["status"] == "pending"

        # Rachel accepts
        accepted = accept_invitation(client, inv["token"], password="Rachel123!")
        assert accepted["name"] == "Rachel Wong"
        assert accepted["org_id"] == self.ORG

        # Rachel can now log in
        rachel_hdrs = auth_headers(client, "rachel.wong@gmail.com", "Rachel123!")
        resp = client.get("/api/v1/people/me", headers=rachel_hdrs)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Rachel Wong"
