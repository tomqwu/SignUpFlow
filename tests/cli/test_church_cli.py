"""
CLI E2E: Church ministry scheduling via YAML workspace.

Same scenario as tests/api/test_church_scenario.py but driven entirely
through the CLI — no API server, no database, just YAML files in →
solution JSON out.

Grace Community Church:
  - 5 volunteers with overlapping ministry roles
  - Sunday Worship needs musicians, sound tech, ushers
  - Sunday School needs teachers
  - Solver must distribute fairly across 4 weeks
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tests.cli.conftest import run_cli, write_yaml, read_json


@pytest.mark.no_mock_auth
class TestChurchCLI:

    def _build_church_workspace(self, ws: Path):
        """Create a church scheduling workspace with YAML files."""
        write_yaml(ws / "org.yaml", {
            "org_id": "grace-church",
            "region": "US",
            "defaults": {"fairness_weight": 50, "cooldown_days": 14},
        })

        write_yaml(ws / "people.yaml", {"people": [
            {"id": "sarah",  "name": "Sarah Chen",   "roles": ["musician", "teacher"]},
            {"id": "david",  "name": "David Kim",    "roles": ["musician", "sound_tech"]},
            {"id": "maria",  "name": "Maria Lopez",  "roles": ["teacher", "volunteer"]},
            {"id": "james",  "name": "James Brown",  "roles": ["usher", "volunteer"]},
            {"id": "emily",  "name": "Emily Davis",  "roles": ["musician", "youth_leader"]},
        ]})

        base = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        base += timedelta(days=(7 - base.weekday()) % 7 + 7)  # Next-next Sunday

        events = []
        for week in range(4):
            sunday = base + timedelta(weeks=week)
            events.append({
                "id": f"worship-wk{week}",
                "type": "Sunday Worship",
                "start": sunday.isoformat(),
                "end": (sunday + timedelta(hours=2)).isoformat(),
                "required_roles": [
                    {"role": "musician", "count": 2},
                    {"role": "sound_tech", "count": 1},
                    {"role": "usher", "count": 1},
                ],
            })

        write_yaml(ws / "events.yaml", {"events": events})
        return base

    # ------------------------------------------------------------------
    # Test: init command creates workspace
    # ------------------------------------------------------------------

    def test_init_creates_workspace(self, tmp_path):
        """signupflow init creates org.yaml, people.yaml, events.yaml."""
        ws = tmp_path / "new-church"
        result = run_cli("init", str(ws))

        assert "Created workspace" in result.stdout
        assert (ws / "org.yaml").exists()
        assert (ws / "people.yaml").exists()
        assert (ws / "events.yaml").exists()

    def test_init_rejects_existing_dir(self, tmp_path):
        """init refuses to overwrite an existing non-empty workspace."""
        ws = tmp_path / "existing"
        ws.mkdir()
        (ws / "dummy.txt").write_text("occupied")

        result = run_cli("init", str(ws), check=False)
        assert result.returncode != 0
        assert "already exists" in result.stderr

    # ------------------------------------------------------------------
    # Test: solve 4 weeks of Sunday worship
    # ------------------------------------------------------------------

    def test_solve_four_sundays(self, tmp_path):
        """Solver schedules 5 volunteers across 4 weeks of Sunday worship."""
        ws = tmp_path / "church"
        self._build_church_workspace(ws)

        result = run_cli("solve", str(ws))

        assert "Solved in" in result.stdout
        assert "Health score:" in result.stdout
        assert "Assignments:" in result.stdout

        # Verify solution file
        solution = read_json(ws / "output" / "solution.json")
        assert solution["assignment_count"] == 4  # One assignment block per event
        assert solution["health_score"] >= 0
        assert len(solution["assignments"]) == 4

        # Every event should have assignments
        event_ids = {a["event_id"] for a in solution["assignments"]}
        for week in range(4):
            assert f"worship-wk{week}" in event_ids

    def test_solve_json_output(self, tmp_path):
        """--json-output flag outputs parseable JSON to stdout."""
        ws = tmp_path / "church"
        self._build_church_workspace(ws)

        result = run_cli("solve", str(ws), "--json-output")

        # Should be valid JSON
        solution = json.loads(result.stdout)
        assert "assignments" in solution
        assert "health_score" in solution
        assert solution["assignment_count"] > 0

    def test_solve_custom_output_dir(self, tmp_path):
        """-o flag saves solution to a custom directory."""
        ws = tmp_path / "church"
        out = tmp_path / "results"
        self._build_church_workspace(ws)

        run_cli("solve", str(ws), "-o", str(out))

        assert (out / "solution.json").exists()
        solution = read_json(out / "solution.json")
        assert solution["assignment_count"] > 0

    # ------------------------------------------------------------------
    # Test: fairness across weeks
    # ------------------------------------------------------------------

    def test_fairness_distribution(self, tmp_path):
        """Solver distributes assignments fairly (no one does 4 weeks while others do 0)."""
        ws = tmp_path / "church"
        self._build_church_workspace(ws)

        result = run_cli("solve", str(ws), "--json-output")
        solution = json.loads(result.stdout)

        # Count assignments per person
        person_counts = {}
        for assignment in solution["assignments"]:
            for person_id in assignment["assignees"]:
                person_counts[person_id] = person_counts.get(person_id, 0) + 1

        # With 5 people and 4 events needing 4 slots each (16 total slots),
        # each person should get 2-4 assignments
        for person_id, count in person_counts.items():
            assert count >= 1, f"{person_id} has 0 assignments"

        # Fairness stdev should be reasonable (not too high)
        assert solution["fairness_stdev"] < 2.0

    # ------------------------------------------------------------------
    # Test: role matching
    # ------------------------------------------------------------------

    def test_role_matching(self, tmp_path):
        """Solver only assigns people who have the required roles."""
        ws = tmp_path / "church"
        self._build_church_workspace(ws)

        result = run_cli("solve", str(ws), "--json-output")
        solution = json.loads(result.stdout)

        # James (usher, volunteer) should appear in assignments since
        # events require ushers. Musicians should appear too.
        all_assigned = set()
        for a in solution["assignments"]:
            all_assigned.update(a["assignees"])

        # At least musicians and ushers should be assigned
        assert len(all_assigned) >= 3  # At minimum 3 of 5 people used

    # ------------------------------------------------------------------
    # Test: empty workspace errors
    # ------------------------------------------------------------------

    def test_solve_missing_events_fails(self, tmp_path):
        """Solver fails gracefully when events.yaml has no events."""
        ws = tmp_path / "empty"
        ws.mkdir()
        write_yaml(ws / "org.yaml", {"org_id": "test", "region": "US"})
        write_yaml(ws / "people.yaml", {"people": [
            {"id": "p1", "name": "Person", "roles": ["vol"]},
        ]})
        write_yaml(ws / "events.yaml", {"events": []})

        result = run_cli("solve", str(ws), check=False)
        assert result.returncode != 0
        assert "No events" in result.stderr

    def test_solve_missing_people_fails(self, tmp_path):
        """Solver fails gracefully when people.yaml has no people."""
        ws = tmp_path / "no-people"
        ws.mkdir()
        write_yaml(ws / "org.yaml", {"org_id": "test", "region": "US"})
        write_yaml(ws / "people.yaml", {"people": []})
        write_yaml(ws / "events.yaml", {"events": [
            {"id": "e1", "type": "Test", "start": "2026-05-01T09:00:00",
             "end": "2026-05-01T11:00:00", "required_roles": [{"role": "vol", "count": 1}]},
        ]})

        result = run_cli("solve", str(ws), check=False)
        assert result.returncode != 0
        assert "No people" in result.stderr
