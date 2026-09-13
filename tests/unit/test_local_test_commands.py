"""Keep complete validation available locally without hosted CI."""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.unit


def test_static_validation_commands_are_documented_locally():
    commands = (ROOT / "docs/TESTING.md").read_text()
    assert "No CI checks" in commands
    for command in ("black --check api tests", "ruff check api tests", "mypy api"):
        assert command in commands
    assert "alembic upgrade head" in commands


def test_mobile_validation_commands_are_documented_locally():
    commands = (ROOT / "mobile/README.md").read_text()
    assert "flutter analyze" in commands
    assert "flutter test" in commands
    assert "no CI checks" in commands


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
