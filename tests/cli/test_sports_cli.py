"""CLI E2E coverage for a Basketball team YAML workspace."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tests.cli.conftest import run_cli, write_yaml


@pytest.mark.no_mock_auth
class TestBasketballCLI:
    """Exercise Basketball roster generation through the public CLI."""

    def _build_workspace(self, workspace: Path, *, tournament: bool = False) -> datetime:
        """Create a Basketball workspace with two qualified players per position."""
        write_yaml(
            workspace / "org.yaml",
            {
                "org_id": "riverside-basketball",
                "region": "CA-ON",
                "defaults": {"fairness_weight": 60},
            },
        )
        positions = (
            "point_guard",
            "shooting_guard",
            "small_forward",
            "power_forward",
            "center",
        )
        people = []
        for position in positions:
            label = position.replace("_", " ").title()
            people.extend(
                [
                    {
                        "id": f"{position}-a",
                        "name": f"{label} A",
                        "roles": [position],
                    },
                    {
                        "id": f"{position}-b",
                        "name": f"{label} B",
                        "roles": [position],
                    },
                ]
            )
        people[0]["roles"].append("shooting_guard")
        people[3]["roles"].append("point_guard")
        write_yaml(workspace / "people.yaml", {"people": people})

        base = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
        base += timedelta(days=14)
        event_count = 5 if tournament else 3
        events = []
        for index in range(event_count):
            start = base + timedelta(days=index)
            events.append(
                {
                    "id": f"basketball-{'tournament' if tournament else 'game'}-{index + 1}",
                    "type": "Basketball tournament game" if tournament else "Basketball game",
                    "start": start.isoformat(),
                    "end": (start + timedelta(hours=2)).isoformat(),
                    "required_roles": [{"role": position, "count": 1} for position in positions],
                }
            )
        write_yaml(workspace / "events.yaml", {"events": events})
        return base

    def test_regular_games_are_fully_scheduled(self, tmp_path: Path) -> None:
        """The solver returns one complete assignment block for every game."""
        workspace = tmp_path / "basketball"
        self._build_workspace(workspace)

        solution = json.loads(run_cli("solve", str(workspace), "--json-output").stdout)

        assert solution["assignment_count"] == 3
        assert solution["hard_violations"] == 0
        assert {row["event_id"] for row in solution["assignments"]} == {
            "basketball-game-1",
            "basketball-game-2",
            "basketball-game-3",
        }
        assert all(len(row["assignees"]) == 5 for row in solution["assignments"])

    def test_multi_position_players_still_fill_one_slot_per_game(self, tmp_path: Path) -> None:
        """A multi-position player cannot occupy two positions in one event."""
        workspace = tmp_path / "basketball"
        self._build_workspace(workspace)

        solution = json.loads(run_cli("solve", str(workspace), "--json-output").stdout)

        for assignment in solution["assignments"]:
            assert len(assignment["assignees"]) == len(set(assignment["assignees"]))
            assert set(assignment["assigned_roles"]) == set(assignment["assignees"])

    def test_tournament_load_is_complete(self, tmp_path: Path) -> None:
        """Five consecutive tournament games remain fully covered."""
        workspace = tmp_path / "tournament"
        self._build_workspace(workspace, tournament=True)

        solution = json.loads(run_cli("solve", str(workspace), "--json-output").stdout)

        assert solution["assignment_count"] == 5
        assert solution["hard_violations"] == 0
        assert all(len(row["assignees"]) == 5 for row in solution["assignments"])

    def test_tournament_load_is_shared(self, tmp_path: Path) -> None:
        """Interchangeable players all receive work during the tournament."""
        workspace = tmp_path / "tournament"
        self._build_workspace(workspace, tournament=True)

        solution = json.loads(run_cli("solve", str(workspace), "--json-output").stdout)
        assigned = {
            person_id
            for assignment in solution["assignments"]
            for person_id in assignment["assignees"]
        }

        assert len(assigned) == 10
        assert solution["fairness_stdev"] < 1.0

    def test_date_range_selects_one_game(self, tmp_path: Path) -> None:
        """The documented date filters limit the solve horizon."""
        workspace = tmp_path / "basketball"
        base = self._build_workspace(workspace)
        day = base.date().isoformat()

        solution = json.loads(
            run_cli(
                "solve",
                str(workspace),
                "--from-date",
                day,
                "--to-date",
                day,
                "--json-output",
            ).stdout
        )

        assert solution["assignment_count"] == 1
        assert solution["assignments"][0]["event_id"] == "basketball-game-1"

    def test_human_output_names_players(self, tmp_path: Path) -> None:
        """Default output reports readable workspace and player details."""
        workspace = tmp_path / "basketball"
        self._build_workspace(workspace)

        result = run_cli("solve", str(workspace))

        assert "People:    10" in result.stdout
        assert "Events:    3" in result.stdout
        assert "Solved in" in result.stdout
        assert "Point Guard" in result.stdout

    def test_strict_mode_is_supported(self, tmp_path: Path) -> None:
        """Strict mode accepts the complete Basketball workspace."""
        workspace = tmp_path / "basketball"
        self._build_workspace(workspace)

        solution = json.loads(
            run_cli("solve", str(workspace), "--mode", "strict", "--json-output").stdout
        )

        assert solution["assignment_count"] == 3
        assert solution["hard_violations"] == 0
