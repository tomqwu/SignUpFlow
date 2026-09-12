"""Keep hosted static checks separate from the complete local test suite."""

import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.unit


def test_hosted_ci_has_static_checks_without_test_execution():
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    assert set(workflow["jobs"]) == {"ci"}
    job = workflow["jobs"]["ci"]
    assert job["name"] == "Lint and type-check"
    commands = "\n".join(step.get("run", "") for step in job["steps"])
    for command in ("black --check api tests", "ruff check api tests", "mypy api"):
        assert command in commands
    assert "pytest" not in commands
    assert "playwright" not in commands
    # Keep the production database migration smoke check, not pytest execution.
    assert "alembic upgrade head" in commands


def test_mobile_ci_analyzes_without_running_tests():
    workflow = yaml.safe_load((ROOT / ".github/workflows/mobile-ci.yml").read_text())
    commands = "\n".join(step.get("run", "") for step in workflow["jobs"]["flutter"]["steps"])
    assert "flutter analyze" in commands
    assert "flutter test" not in commands


def test_local_all_runs_each_python_tier_in_a_separate_process():
    result = subprocess.run(
        ["make", "-n", "test-all"], cwd=ROOT, text=True, capture_output=True, check=True
    )
    commands = [line for line in result.stdout.splitlines() if "poetry run pytest " in line]
    assert len(commands) == 7
    for tier in ("unit", "api", "cli", "integration", "web", "contract", "e2e"):
        assert sum(f"pytest tests/{tier}/ " in command for command in commands) == 1


def test_local_mobile_target_runs_flutter_tests():
    result = subprocess.run(
        ["make", "-n", "test-mobile"], cwd=ROOT, text=True, capture_output=True, check=True
    )
    assert "flutter test" in result.stdout
