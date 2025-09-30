"""Test stats and metrics computation."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from roster_cli.core.loader import load_solution
from roster_cli.main import app

runner = CliRunner()


@pytest.fixture
def church_workspace_with_solution(tmp_path: Path) -> Path:
    """Create church workspace with solution."""
    workspace = tmp_path / "church"
    result = runner.invoke(app, ["init", "--dir", str(workspace), "--template", "church"])
    assert result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "solve",
            "--dir",
            str(workspace),
            "--from",
            "2025-09-01",
            "--to",
            "2025-10-31",
        ],
    )
    assert result.exit_code == 0

    return workspace


def test_metrics_computed(church_workspace_with_solution: Path) -> None:
    """Test that all metrics are computed."""
    solution = load_solution(church_workspace_with_solution / "out" / "solution.json")

    assert solution.metrics.solve_ms > 0
    assert solution.metrics.hard_violations >= 0
    assert solution.metrics.soft_score >= 0
    assert solution.metrics.fairness.stdev >= 0
    assert 0 <= solution.metrics.health_score <= 100


def test_health_score_range(church_workspace_with_solution: Path) -> None:
    """Test health score is in valid range."""
    solution = load_solution(church_workspace_with_solution / "out" / "solution.json")

    assert 0 <= solution.metrics.health_score <= 100

    if solution.metrics.hard_violations > 0:
        assert solution.metrics.health_score == 0
    else:
        assert solution.metrics.health_score > 0


def test_fairness_metrics(church_workspace_with_solution: Path) -> None:
    """Test fairness metrics are computed."""
    solution = load_solution(church_workspace_with_solution / "out" / "solution.json")

    fairness = solution.metrics.fairness
    assert isinstance(fairness.per_person_counts, dict)
    assert fairness.stdev >= 0

    # Check that counts are reasonable
    total_assignments = sum(fairness.per_person_counts.values())
    assert total_assignments > 0


def test_stats_command(church_workspace_with_solution: Path) -> None:
    """Test stats command displays metrics."""
    solution_path = church_workspace_with_solution / "out" / "solution.json"

    result = runner.invoke(app, ["stats", "--solution", str(solution_path)])

    assert result.exit_code == 0
    assert "Solution Statistics" in result.stdout
    assert "Health score" in result.stdout
    assert "Fairness" in result.stdout
