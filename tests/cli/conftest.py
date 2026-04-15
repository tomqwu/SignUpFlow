"""CLI E2E test fixtures.

Tests run the CLI as a subprocess (like a real user would) against
YAML workspace directories created in tmp_path.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


@pytest.fixture(autouse=True)
def mock_authentication():
    """Suppress root conftest auth mocking — CLI tests don't use the API."""
    yield


@pytest.fixture(autouse=True)
def reset_database_between_tests():
    """Suppress root conftest DB reset — CLI tests use YAML files, not DB."""
    yield


def run_cli(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run signupflow CLI and return result."""
    cmd = [sys.executable, "-m", "api.cli.main"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if check and result.returncode != 0:
        raise AssertionError(
            f"CLI failed (exit {result.returncode}):\n"
            f"  cmd: {' '.join(args)}\n"
            f"  stderr: {result.stderr}\n"
            f"  stdout: {result.stdout}"
        )
    return result


def write_yaml(path: Path, data: dict):
    """Write a dict as YAML to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def read_json(path: Path) -> dict:
    """Read a JSON file and return as dict."""
    with open(path) as f:
        return json.load(f)
