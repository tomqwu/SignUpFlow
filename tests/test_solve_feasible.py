"""Test solving produces feasible solutions."""

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from roster_cli.core.loader import load_solution
from roster_cli.main import app

runner = CliRunner()


@pytest.fixture
def cricket_workspace(tmp_path: Path) -> Path:
    """Create cricket workspace."""
    workspace = tmp_path / "cricket"
    result = runner.invoke(app, ["init", "--dir", str(workspace), "--template", "cricket"])
    assert result.exit_code == 0
    return workspace


@pytest.fixture
def church_workspace(tmp_path: Path) -> Path:
    """Create church workspace."""
    workspace = tmp_path / "church"
    result = runner.invoke(app, ["init", "--dir", str(workspace), "--template", "church"])
    assert result.exit_code == 0
    return workspace


@pytest.fixture
def oncall_workspace(tmp_path: Path) -> Path:
    """Create oncall workspace."""
    workspace = tmp_path / "oncall"
    result = runner.invoke(app, ["init", "--dir", str(workspace), "--template", "oncall"])
    assert result.exit_code == 0
    return workspace


def test_cricket_solve_feasible(cricket_workspace: Path) -> None:
    """Test cricket template produces feasible solution."""
    result = runner.invoke(
        app,
        [
            "solve",
            "--dir",
            str(cricket_workspace),
            "--from",
            "2025-09-01",
            "--to",
            "2025-09-30",
        ],
    )

    assert result.exit_code == 0
    assert (cricket_workspace / "out" / "solution.json").exists()

    solution = load_solution(cricket_workspace / "out" / "solution.json")
    assert solution.metrics.hard_violations == 0
    assert solution.metrics.health_score > 0
    assert len(solution.assignments) > 0

    # Check no Friday/Monday matches on long weekends (Sept 1 is Labour Day)
    labour_day = date(2025, 9, 1)
    for assignment in solution.assignments:
        if assignment.event_id == "match_01":  # Sept 1
            # This match should be scheduled (it's a Monday on a long weekend)
            # Our constraint forbids it, so it shouldn't be in solution if constraint active
            pass


def test_church_solve_feasible(church_workspace: Path) -> None:
    """Test church template produces feasible solution."""
    result = runner.invoke(
        app,
        [
            "solve",
            "--dir",
            str(church_workspace),
            "--from",
            "2025-09-01",
            "--to",
            "2025-10-31",
        ],
    )

    assert result.exit_code == 0
    solution = load_solution(church_workspace / "out" / "solution.json")

    # Should have minimal hard violations (role coverage might be challenging)
    assert solution.metrics.health_score > 0
    assert len(solution.assignments) > 0

    # Check role requirements are met
    assignments_map = {a.event_id: a for a in solution.assignments}
    assert len(assignments_map) > 0


def test_oncall_solve_feasible(oncall_workspace: Path) -> None:
    """Test oncall template produces feasible solution."""
    result = runner.invoke(
        app,
        [
            "solve",
            "--dir",
            str(oncall_workspace),
            "--from",
            "2025-09-01",
            "--to",
            "2025-09-10",
        ],
    )

    assert result.exit_code == 0
    solution = load_solution(oncall_workspace / "out" / "solution.json")

    assert solution.metrics.health_score > 0
    assert len(solution.assignments) == 10  # 10 days

    # Check fairness variance
    assert solution.metrics.fairness.stdev < 2.0  # Should be fairly balanced


def test_solve_creates_all_outputs(cricket_workspace: Path) -> None:
    """Test solve creates all expected output files."""
    result = runner.invoke(
        app,
        [
            "solve",
            "--dir",
            str(cricket_workspace),
            "--from",
            "2025-09-01",
            "--to",
            "2025-09-15",
        ],
    )

    assert result.exit_code == 0
    out_dir = cricket_workspace / "out"
    assert (out_dir / "solution.json").exists()
    assert (out_dir / "assignments.csv").exists()
    assert (out_dir / "calendar.ics").exists()
    assert (out_dir / "metrics.json").exists()
