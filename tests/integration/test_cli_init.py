"""Test CLI init command."""

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from roster_cli.main import app

runner = CliRunner()


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """Create temporary workspace."""
    workspace = tmp_path / "test_workspace"
    yield workspace
    if workspace.exists():
        shutil.rmtree(workspace)


def test_init_cricket_template(temp_workspace: Path) -> None:
    """Test initializing cricket template."""
    result = runner.invoke(app, ["init", "--dir", str(temp_workspace), "--template", "cricket"])

    assert result.exit_code == 0
    assert temp_workspace.exists()
    assert (temp_workspace / "org.yaml").exists()
    assert (temp_workspace / "teams.yaml").exists()
    assert (temp_workspace / "people.yaml").exists()
    assert (temp_workspace / "events.yaml").exists()
    assert (temp_workspace / "constraints").is_dir()


def test_init_church_template(temp_workspace: Path) -> None:
    """Test initializing church template."""
    result = runner.invoke(app, ["init", "--dir", str(temp_workspace), "--template", "church"])

    assert result.exit_code == 0
    assert temp_workspace.exists()
    assert (temp_workspace / "org.yaml").exists()
    assert (temp_workspace / "people.yaml").exists()
    assert (temp_workspace / "constraints" / "require_role_coverage.yaml").exists()


def test_init_oncall_template(temp_workspace: Path) -> None:
    """Test initializing oncall template."""
    result = runner.invoke(app, ["init", "--dir", str(temp_workspace), "--template", "oncall"])

    assert result.exit_code == 0
    assert temp_workspace.exists()
    assert (temp_workspace / "org.yaml").exists()
    assert (temp_workspace / "people.yaml").exists()
    assert (temp_workspace / "events.yaml").exists()


def test_init_invalid_template(temp_workspace: Path) -> None:
    """Test initializing with invalid template."""
    result = runner.invoke(app, ["init", "--dir", str(temp_workspace), "--template", "invalid"])

    assert result.exit_code == 1
