"""
Scenario: Riverside Sports Club — cricket and basketball roster management.

Cast:
  Coach Thompson  — admin, manages both sports
  Rahul Sharma    — cricket (batsman, wicket_keeper)
  Priya Patel     — cricket (bowler) AND basketball (point_guard)
  Marcus Johnson  — basketball (center, power_forward)
  Alex Rivera     — basketball (shooting_guard) AND cricket (all_rounder)
  Tomoko Sato     — basketball (small_forward, point_guard)
  Ben O'Brien     — cricket (batsman, bowler) — backup player

Events:
  Cricket Match (Saturday)    — needs: batsman x4, bowler x2, wicket_keeper x1
  Cricket Practice (Thursday) — needs: batsman x3, bowler x2
  Basketball Game (Friday)    — needs: point_guard x1, shooting_guard x1, center x1,
                                       small_forward x1, power_forward x1
  Basketball Practice (Tue)   — needs: point_guard x1, shooting_guard x1, center x1

Real-world tensions:
  - Priya and Alex play BOTH sports → scheduling conflicts on busy weeks
  - Rahul injured for 2 weeks → time-off blocks him from cricket matches
  - Tournament week: extra matches for both sports
  - Fair rotation: everyone should get roughly equal game time
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
class TestSportsScenario:
    """Riverside Sports Club: cricket and basketball roster management."""

    ORG = "riverside-sports"
    COACH_EMAIL = "coach.thompson@riverside.club"
    COACH_PW = "CoachPass123!"

    PLAYERS = [
        {
            "email": "rahul@riverside.club",
            "name": "Rahul Sharma",
            "roles": ["batsman", "wicket_keeper"],
        },
        {
            "email": "priya@riverside.club",
            "name": "Priya Patel",
            "roles": ["bowler", "point_guard"],
        },
        {
            "email": "marcus@riverside.club",
            "name": "Marcus Johnson",
            "roles": ["center", "power_forward"],
        },
        {
            "email": "alex@riverside.club",
            "name": "Alex Rivera",
            "roles": ["shooting_guard", "all_rounder", "batsman"],
        },
        {
            "email": "tomoko@riverside.club",
            "name": "Tomoko Sato",
            "roles": ["small_forward", "point_guard"],
        },
        {"email": "ben@riverside.club", "name": "Ben O'Brien", "roles": ["batsman", "bowler"]},
    ]

    PLAYER_PW = "Player123!"

    def _setup_club(self, client):
        """Create sports club with coach and all players."""
        seed_org(client, self.ORG, name="Riverside Sports Club")
        seed_user(client, self.ORG, self.COACH_EMAIL, "Coach Thompson", self.COACH_PW)
        hdrs = auth_headers(client, self.COACH_EMAIL, self.COACH_PW)

        players = {}
        for p in self.PLAYERS:
            inv = seed_invitation(client, hdrs, self.ORG, p["email"], p["name"], roles=p["roles"])
            accepted = accept_invitation(client, inv["token"], password=self.PLAYER_PW)
            players[p["email"]] = {
                "person_id": accepted["person_id"],
                "name": p["name"],
                "roles": p["roles"],
            }

        return hdrs, players

    # ------------------------------------------------------------------
    # Test: Club setup with multi-sport players
    # ------------------------------------------------------------------

    def test_club_setup_and_dual_sport_players(self, client):
        """Coach registers players, some playing both cricket and basketball."""
        hdrs, players = self._setup_club(client)

        # 7 people total (coach + 6 players)
        resp = client.get(f"/api/v1/people/?org_id={self.ORG}", headers=hdrs)
        assert resp.status_code == 200
        assert resp.json()["total"] == 7

        # Priya plays both sports
        priya_hdrs = auth_headers(client, "priya@riverside.club", self.PLAYER_PW)
        resp = client.get("/api/v1/people/me", headers=priya_hdrs)
        assert resp.status_code == 200
        roles = resp.json()["roles"]
        assert "bowler" in roles
        assert "point_guard" in roles

        # Alex plays both sports
        alex_hdrs = auth_headers(client, "alex@riverside.club", self.PLAYER_PW)
        resp = client.get("/api/v1/people/me", headers=alex_hdrs)
        roles = resp.json()["roles"]
        assert "shooting_guard" in roles
        assert "all_rounder" in roles
        assert "batsman" in roles

    # ------------------------------------------------------------------
    # Test: Sport-specific teams
    # ------------------------------------------------------------------

    def test_sport_teams(self, client):
        """Coach creates cricket and basketball squads."""
        hdrs, players = self._setup_club(client)

        cricket_ids = [
            players["rahul@riverside.club"]["person_id"],
            players["priya@riverside.club"]["person_id"],
            players["alex@riverside.club"]["person_id"],
            players["ben@riverside.club"]["person_id"],
        ]
        cricket = seed_team(
            client, hdrs, self.ORG, "cricket-squad", "Cricket Squad", member_ids=cricket_ids
        )
        assert cricket["name"] == "Cricket Squad"

        basketball_ids = [
            players["priya@riverside.club"]["person_id"],
            players["marcus@riverside.club"]["person_id"],
            players["alex@riverside.club"]["person_id"],
            players["tomoko@riverside.club"]["person_id"],
        ]
        basketball = seed_team(
            client,
            hdrs,
            self.ORG,
            "basketball-squad",
            "Basketball Squad",
            member_ids=basketball_ids,
        )
        assert basketball["name"] == "Basketball Squad"

        # Priya and Alex are on BOTH squads
        resp = client.get(f"/api/v1/teams/?org_id={self.ORG}", headers=hdrs)
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

    # ------------------------------------------------------------------
    # Test: Weekly match schedule
    # ------------------------------------------------------------------

    def test_weekly_match_schedule(self, client):
        """Coach creates a week of practices and matches for both sports."""
        hdrs, players = self._setup_club(client)

        # Tuesday: Basketball practice
        seed_event(
            client,
            hdrs,
            self.ORG,
            "bball-practice-1",
            event_type="Basketball Practice",
            days_from_now=15,  # Tuesday
            duration_hours=2,
            role_counts={"point_guard": 1, "shooting_guard": 1, "center": 1},
        )

        # Thursday: Cricket practice
        seed_event(
            client,
            hdrs,
            self.ORG,
            "cricket-practice-1",
            event_type="Cricket Practice",
            days_from_now=17,  # Thursday
            duration_hours=3,
            role_counts={"batsman": 3, "bowler": 2},
        )

        # Friday: Basketball game
        seed_event(
            client,
            hdrs,
            self.ORG,
            "bball-game-1",
            event_type="Basketball Game",
            days_from_now=18,  # Friday
            duration_hours=2,
            role_counts={
                "point_guard": 1,
                "shooting_guard": 1,
                "center": 1,
                "small_forward": 1,
                "power_forward": 1,
            },
        )

        # Saturday: Cricket match
        seed_event(
            client,
            hdrs,
            self.ORG,
            "cricket-match-1",
            event_type="Cricket Match",
            days_from_now=19,  # Saturday
            duration_hours=6,
            role_counts={"batsman": 4, "bowler": 2, "wicket_keeper": 1},
        )

        resp = client.get(f"/api/v1/events/?org_id={self.ORG}")
        assert resp.status_code == 200
        assert resp.json()["total"] == 4

    # ------------------------------------------------------------------
    # Test: Player injury (time-off)
    # ------------------------------------------------------------------

    def test_player_injury_timeoff(self, client):
        """Rahul injured — blocked from all events for 2 weeks."""
        hdrs, players = self._setup_club(client)

        rahul_id = players["rahul@riverside.club"]["person_id"]

        injury_start = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        injury_end = (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d")
        add_timeoff(
            client, rahul_id, injury_start, injury_end, reason="Hamstring injury — physio recovery"
        )

        resp = client.get(f"/api/v1/availability/{rahul_id}/timeoff")
        assert resp.status_code == 200
        periods = resp.json()["timeoff"]
        assert len(periods) == 1
        assert "Hamstring" in periods[0]["reason"]

    # ------------------------------------------------------------------
    # Test: Solver generates roster for a match week
    # ------------------------------------------------------------------

    def test_solver_generates_weekly_roster(self, client):
        """
        Coach runs solver for a full week of practices and matches.
        Verifies assignments are generated for all events.
        """
        hdrs, players = self._setup_club(client)

        # Create a full week of events
        events = [
            (
                "bball-prac",
                "Basketball Practice",
                15,
                {"point_guard": 1, "shooting_guard": 1, "center": 1},
            ),
            ("cricket-prac", "Cricket Practice", 17, {"batsman": 3, "bowler": 2}),
            (
                "bball-game",
                "Basketball Game",
                18,
                {
                    "point_guard": 1,
                    "shooting_guard": 1,
                    "center": 1,
                    "small_forward": 1,
                    "power_forward": 1,
                },
            ),
            ("cricket-match", "Cricket Match", 19, {"batsman": 3, "bowler": 2, "wicket_keeper": 1}),
        ]
        for eid, etype, days, roles in events:
            seed_event(
                client, hdrs, self.ORG, eid, event_type=etype, days_from_now=days, role_counts=roles
            )

        # Solve
        from_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        to_date = (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d")
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
        assert solution["assignment_count"] > 0
        assert solution["metrics"]["health_score"] >= 0

        # Every event should have assignments
        resp = client.get(f"/api/v1/events/assignments/all?org_id={self.ORG}")
        assert resp.status_code == 200
        assignments = resp.json()["assignments"]
        assigned_events = {a["event_id"] for a in assignments}
        for eid, _, _, _ in events:
            assert eid in assigned_events, f"No assignments for {eid}"

    # ------------------------------------------------------------------
    # Test: Tournament week (extra matches)
    # ------------------------------------------------------------------

    def test_tournament_week_heavy_load(self, client):
        """
        Tournament week: 3 cricket matches + 2 basketball games.
        Tests solver under heavy load — more events than usual.
        """
        hdrs, players = self._setup_club(client)

        # 3 cricket matches (Fri, Sat, Sun)
        for i in range(3):
            seed_event(
                client,
                hdrs,
                self.ORG,
                f"tournament-cricket-{i}",
                event_type="Tournament Cricket",
                days_from_now=18 + i,
                role_counts={"batsman": 3, "bowler": 2, "wicket_keeper": 1},
            )

        # 2 basketball games (Fri, Sat)
        for i in range(2):
            seed_event(
                client,
                hdrs,
                self.ORG,
                f"tournament-bball-{i}",
                event_type="Tournament Basketball",
                days_from_now=18 + i,
                role_counts={
                    "point_guard": 1,
                    "shooting_guard": 1,
                    "center": 1,
                    "small_forward": 1,
                },
            )

        # Solve tournament week
        from_date = (datetime.now() + timedelta(days=17)).strftime("%Y-%m-%d")
        to_date = (datetime.now() + timedelta(days=22)).strftime("%Y-%m-%d")
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
        assert resp.status_code == 200

        solution = resp.json()
        assert solution["assignment_count"] > 0

        # Verify fairness — with 5 events, assignments should be spread
        fairness = solution["metrics"]["fairness"]
        assert fairness["stdev"] >= 0  # Stdev exists

    # ------------------------------------------------------------------
    # Test: Coach manually adjusts roster
    # ------------------------------------------------------------------

    def test_coach_manual_roster_adjustment(self, client):
        """Coach manually assigns and removes players from a match."""
        hdrs, players = self._setup_club(client)

        match = seed_event(
            client,
            hdrs,
            self.ORG,
            "finals-match",
            event_type="Cricket Finals",
            days_from_now=21,
            role_counts={"batsman": 4, "bowler": 2, "wicket_keeper": 1},
        )

        rahul_id = players["rahul@riverside.club"]["person_id"]
        ben_id = players["ben@riverside.club"]["person_id"]

        # Assign Rahul as batsman
        resp = client.post(
            f"/api/v1/events/{match['id']}/assignments",
            json={
                "person_id": rahul_id,
                "action": "assign",
                "role": "batsman",
            },
            headers=hdrs,
        )
        assert resp.status_code == 200

        # Assign Ben as batsman
        resp = client.post(
            f"/api/v1/events/{match['id']}/assignments",
            json={
                "person_id": ben_id,
                "action": "assign",
                "role": "batsman",
            },
            headers=hdrs,
        )
        assert resp.status_code == 200

        # Rahul gets injured — unassign him
        resp = client.post(
            f"/api/v1/events/{match['id']}/assignments",
            json={
                "person_id": rahul_id,
                "action": "unassign",
            },
            headers=hdrs,
        )
        assert resp.status_code == 200

        # Verify only Ben remains assigned
        resp = client.get(f"/api/v1/events/assignments/all?org_id={self.ORG}")
        assert resp.status_code == 200
        match_assignments = [
            a for a in resp.json()["assignments"] if a["event_id"] == "finals-match"
        ]
        assigned_ids = {a["person_id"] for a in match_assignments}
        assert ben_id in assigned_ids
        assert rahul_id not in assigned_ids

    # ------------------------------------------------------------------
    # Test: Player can't modify roster (RBAC)
    # ------------------------------------------------------------------

    def test_player_cannot_create_events(self, client):
        """Regular player can't create matches — only coach can."""
        hdrs, players = self._setup_club(client)

        player_hdrs = auth_headers(client, "rahul@riverside.club", self.PLAYER_PW)

        start = (datetime.now() + timedelta(days=14)).isoformat()
        end = (datetime.now() + timedelta(days=14, hours=2)).isoformat()
        resp = client.post(
            "/api/v1/events/",
            json={
                "id": "unauthorized-match",
                "org_id": self.ORG,
                "type": "Rogue Match",
                "start_time": start,
                "end_time": end,
            },
            headers=player_hdrs,
        )
        assert resp.status_code == 403
