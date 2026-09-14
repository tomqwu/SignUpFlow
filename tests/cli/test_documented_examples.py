"""Smoke the installed CLI and every retained YAML workspace from the public docs."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.cli.conftest import run_cli

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.no_mock_auth
def test_installed_cli_help() -> None:
    """The documented Poetry-installed command resolves and displays its commands."""
    result = subprocess.run(
        ["poetry", "run", "signupflow", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "init" in result.stdout
    assert "solve" in result.stdout


@pytest.mark.no_mock_auth
@pytest.mark.parametrize("domain", ["church", "basketball"])
def test_documented_workspace_solves(domain: str, tmp_path: Path) -> None:
    """Each retained domain workspace loads and solves in a disposable copy."""
    workspace = tmp_path / domain
    shutil.copytree(ROOT / "examples" / domain, workspace)

    result = run_cli("solve", str(workspace), "--json-output")
    solution = json.loads(result.stdout)

    assert solution["assignment_count"] == 12
    assert solution["hard_violations"] == 0
    assert (workspace / "output").exists() is False
