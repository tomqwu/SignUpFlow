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
    api_command = next(command for command in commands if "pytest tests/api/ " in command)
    assert "tests/security/" in api_command


def test_make_test_uses_the_supported_complete_local_suite():
    result = subprocess.run(
        ["make", "-n", "test"], cwd=ROOT, text=True, capture_output=True, check=True
    )

    assert "tests/comprehensive_test_suite.py" not in result.stdout
    for tier in ("unit", "api", "cli", "integration", "web", "contract", "e2e"):
        assert f"pytest tests/{tier}/ " in result.stdout
    assert "pytest tests/api/ tests/security/" in result.stdout


def test_playwright_is_a_locked_development_dependency():
    project = (ROOT / "pyproject.toml").read_text()
    lock = (ROOT / "poetry.lock").read_text()

    assert 'playwright = "' in project
    assert 'name = "playwright"' in lock


def test_python_preflight_matches_the_project_range():
    makefile = (ROOT / "Makefile").read_text()

    assert "poetry run python --version" in makefile
    assert "Python 3.11 through 3.13 required" in makefile
    assert '"$$PY_MINOR" -gt 13' in makefile


def test_local_mobile_target_runs_flutter_tests():
    result = subprocess.run(
        ["make", "-n", "test-mobile"], cwd=ROOT, text=True, capture_output=True, check=True
    )
    assert "flutter test" in result.stdout
