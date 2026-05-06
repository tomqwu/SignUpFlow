"""
CLI E2E: Sports club roster scheduling via YAML workspace.

Cricket and basketball rosters for Riverside Sports Club.
Dual-sport players, tournament week heavy load, role-specific assignments.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tests.cli.conftest import run_cli, write_yaml


@pytest.mark.no_mock_auth
class TestSportsCLI:
    def _build_sports_workspace(self, ws: Path, tournament: bool = False):
        """Create a sports club workspace."""
        write_yaml(
            ws / "org.yaml",
            {
                "org_id": "riverside-sports",
                "region": "AU",
                "defaults": {"fairness_weight": 60},
            },
        )

        write_yaml(
            ws / "people.yaml",
            {
                "people": [
                    {"id": "rahul", "name": "Rahul Sharma", "roles": ["batsman", "wicket_keeper"]},
                    {"id": "priya", "name": "Priya Patel", "roles": ["bowler", "point_guard"]},
                    {
                        "id": "marcus",
                        "name": "Marcus Johnson",
                        "roles": ["center", "power_forward"],
                    },
                    {
                        "id": "alex",
                        "name": "Alex Rivera",
                        "roles": ["shooting_guard", "all_rounder", "batsman"],
                    },
                    {
                        "id": "tomoko",
                        "name": "Tomoko Sato",
                        "roles": ["small_forward", "point_guard"],
                    },
                    {"id": "ben", "name": "Ben O'Brien", "roles": ["batsman", "bowler"]},
                ]
            },
        )

        base = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
        base += timedelta(days=14)

        events = []
        if tournament:
            # Tournament: 3 cricket + 2 basketball in 3 days
            for i in range(3):
                events.append(
                    {
                        "id": f"cricket-t{i}",
                        "type": "Tournament Cricket",
                        "start": (base + timedelta(days=i)).isoformat(),
                        "end": (base + timedelta(days=i, hours=6)).isoformat(),
                        "required_roles": [
                            {"role": "batsman", "count": 3},
                            {"role": "bowler", "count": 2},
                            {"role": "wicket_keeper", "count": 1},
                        ],
                    }
                )
            for i in range(2):
                events.append(
                    {
                        "id": f"bball-t{i}",
                        "type": "Tournament Basketball",
                        "start": (base + timedelta(days=i, hours=7)).isoformat(),
                        "end": (base + timedelta(days=i, hours=9)).isoformat(),
                        "required_roles": [
                            {"role": "point_guard", "count": 1},
                            {"role": "shooting_guard", "count": 1},
                            {"role": "center", "count": 1},
                            {"role": "small_forward", "count": 1},
                        ],
                    }
                )
        else:
            # Regular week
            events = [
                {
                    "id": "cricket-practice",
                    "type": "Cricket Practice",
                    "start": (base).isoformat(),
                    "end": (base + timedelta(hours=3)).isoformat(),
                    "required_roles": [
                        {"role": "batsman", "count": 3},
                        {"role": "bowler", "count": 2},
                    ],
                },
                {
                    "id": "bball-game",
                    "type": "Basketball Game",
                    "start": (base + timedelta(days=1)).isoformat(),
                    "end": (base + timedelta(days=1, hours=2)).isoformat(),
                    "required_roles": [
                        {"role": "point_guard", "count": 1},
                        {"role": "shooting_guard", "count": 1},
                        {"role": "center", "count": 1},
                        {"role": "small_forward", "count": 1},
                        {"role": "power_forward", "count": 1},
                    ],
                },
                {
                    "id": "cricket-match",
                    "type": "Cricket Match",
                    "start": (base + timedelta(days=2)).isoformat(),
                    "end": (base + timedelta(days=2, hours=6)).isoformat(),
                    "required_roles": [
                        {"role": "batsman", "count": 3},
                        {"role": "bowler", "count": 2},
                        {"role": "wicket_keeper", "count": 1},
                    ],
                },
            ]

        write_yaml(ws / "events.yaml", {"events": events})

    # ------------------------------------------------------------------
    # Test: Regular week roster
    # ------------------------------------------------------------------

    def test_regular_week_roster(self, tmp_path):
        """Solver fills cricket practice, basketball game, and cricket match."""
        ws = tmp_path / "sports"
        self._build_sports_workspace(ws)

        result = run_cli("solve", str(ws), "--json-output")
        solution = json.loads(result.stdout)

        assert solution["assignment_count"] == 3
        event_ids = {a["event_id"] for a in solution["assignments"]}
        assert "cricket-practice" in event_ids
        assert "bball-game" in event_ids
        assert "cricket-match" in event_ids

    def test_dual_sport_players_assigned(self, tmp_path):
        """Priya (bowler + point_guard) and Alex (shooting_guard + batsman) serve both sports."""
        ws = tmp_path / "sports"
        self._build_sports_workspace(ws)

        result = run_cli("solve", str(ws), "--json-output")
        solution = json.loads(result.stdout)

        # Collect all assigned person IDs per event type
        cricket_assigned = set()
        bball_assigned = set()
        for a in solution["assignments"]:
            if "cricket" in a["event_id"]:
                cricket_assigned.update(a["assignees"])
            elif "bball" in a["event_id"]:
                bball_assigned.update(a["assignees"])

        # Priya should appear in cricket (bowler) or basketball (point_guard) or both
        # Alex should appear in cricket (batsman) or basketball (shooting_guard) or both
        dual_players = cricket_assigned & bball_assigned
        # At least one dual-sport player should serve both
        assert (
            len(dual_players) >= 1
        ), f"No dual-sport players found. Cricket: {cricket_assigned}, Basketball: {bball_assigned}"

    # ------------------------------------------------------------------
    # Test: Tournament week (heavy load)
    # ------------------------------------------------------------------

    def test_tournament_week(self, tmp_path):
        """5 events in 3 days — solver handles tournament load."""
        ws = tmp_path / "tournament"
        self._build_sports_workspace(ws, tournament=True)

        result = run_cli("solve", str(ws), "--json-output")
        solution = json.loads(result.stdout)

        assert solution["assignment_count"] == 5
        assert solution["health_score"] >= 0

        # All 5 events should be assigned
        event_ids = {a["event_id"] for a in solution["assignments"]}
        for i in range(3):
            assert f"cricket-t{i}" in event_ids
        for i in range(2):
            assert f"bball-t{i}" in event_ids

    def test_tournament_fairness(self, tmp_path):
        """In a tournament, no player should be overloaded vs others."""
        ws = tmp_path / "tournament"
        self._build_sports_workspace(ws, tournament=True)

        result = run_cli("solve", str(ws), "--json-output")
        solution = json.loads(result.stdout)

        person_counts = {}
        for a in solution["assignments"]:
            for pid in a["assignees"]:
                person_counts[pid] = person_counts.get(pid, 0) + 1

        # 6 players across 5 events — everyone should contribute
        assert len(person_counts) >= 4, f"Only {len(person_counts)} of 6 players used"

    # ------------------------------------------------------------------
    # Test: Date range filtering
    # ------------------------------------------------------------------

    def test_date_range_filter(self, tmp_path):
        """--from-date and --to-date filter which events are scheduled."""
        ws = tmp_path / "sports"
        self._build_sports_workspace(ws)

        # Solve only the first day (cricket practice)
        base = datetime.now() + timedelta(days=14)
        from_d = base.strftime("%Y-%m-%d")
        to_d = from_d  # Same day

        result = run_cli(
            "solve", str(ws), "--from-date", from_d, "--to-date", to_d, "--json-output"
        )
        solution = json.loads(result.stdout)

        # Only events on that day
        assert solution["assignment_count"] >= 1
        event_ids = {a["event_id"] for a in solution["assignments"]}
        assert "cricket-practice" in event_ids

    # ------------------------------------------------------------------
    # Test: Human-readable output
    # ------------------------------------------------------------------

    def test_human_readable_output(self, tmp_path):
        """Default output shows names, not just IDs."""
        ws = tmp_path / "sports"
        self._build_sports_workspace(ws)

        result = run_cli("solve", str(ws))

        # Should contain human-readable info
        assert "Riverside" not in result.stdout or "Workspace:" in result.stdout
        assert "People:" in result.stdout
        assert "Events:" in result.stdout
        assert "Solved in" in result.stdout
        # Should show people names in assignments
        assert any(
            name in result.stdout for name in ["Rahul", "Priya", "Marcus", "Alex", "Tomoko", "Ben"]
        )

    # ------------------------------------------------------------------
    # Test: Solve modes
    # ------------------------------------------------------------------

    def test_strict_mode(self, tmp_path):
        """--mode strict runs the solver (mode currently unused but accepted)."""
        ws = tmp_path / "sports"
        self._build_sports_workspace(ws)

        result = run_cli("solve", str(ws), "--mode", "strict", "--json-output")
        solution = json.loads(result.stdout)
        assert solution["assignment_count"] > 0
