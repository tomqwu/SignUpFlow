"""Keep complete validation available locally without hosted CI."""

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.unit


def test_static_validation_commands_are_documented_locally():
    commands = (ROOT / "docs/TESTING.md").read_text()
    assert "No CI checks" in commands
    for command in (
        "black --check api web tests scripts/run_local_validation.py",
        "ruff check api web tests scripts/run_local_validation.py",
        "mypy api",
    ):
        assert command in commands
    assert "make test-postgres" in commands


def test_mobile_validation_commands_are_documented_locally():
    commands = (ROOT / "mobile/README.md").read_text()
    assert "flutter analyze" in commands
    assert "flutter test" in commands
    assert "no CI checks" in commands


def test_local_all_runs_each_python_tier_in_a_separate_process():
    result = subprocess.run(
        ["make", "-n", "test-all"], cwd=ROOT, text=True, capture_output=True, check=True
    )
    assert "scripts/run_local_validation.py" in result.stdout
    manifest = (ROOT / "tests/local_validation_manifest.json").read_text()
    for tier in ("unit", "api", "cli", "integration", "web", "contract", "e2e"):
        assert f'"id": "{tier}"' in manifest
    assert '"tests/security"' in manifest


def test_make_test_uses_the_supported_complete_local_suite():
    result = subprocess.run(
        ["make", "-n", "test"], cwd=ROOT, text=True, capture_output=True, check=True
    )

    assert "tests/comprehensive_test_suite.py" not in result.stdout
    assert "scripts/run_local_validation.py" in result.stdout


def test_current_contributor_and_agent_guides_do_not_name_removed_test_files():
    for path in (ROOT / "CONTRIBUTING.md", ROOT / "CLAUDE.md"):
        assert "tests/comprehensive_test_suite.py" not in path.read_text()


@pytest.mark.parametrize("target", ["test-docker-comprehensive", "test-docker-all"])
def test_retired_docker_full_suite_targets_fail_with_current_guidance(target):
    result = subprocess.run(
        ["make", "-s", target], cwd=ROOT, text=True, capture_output=True, check=False
    )

    assert result.returncode != 0
    assert "run 'make test-all' locally" in result.stdout
    assert "tests/comprehensive_test_suite.py" not in result.stdout + result.stderr


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


def test_local_postgres_target_runs_the_owned_validator():
    result = subprocess.run(
        ["make", "-n", "test-postgres"], cwd=ROOT, text=True, capture_output=True, check=True
    )

    assert "scripts/run_postgres_validation.py" in result.stdout


def test_local_artifact_target_runs_the_owned_validator():
    result = subprocess.run(
        ["make", "-n", "test-artifact"], cwd=ROOT, text=True, capture_output=True, check=True
    )

    assert "scripts/validate_production_artifact.py" in result.stdout
    assert "make test-artifact" in (ROOT / "docs/TESTING.md").read_text()
