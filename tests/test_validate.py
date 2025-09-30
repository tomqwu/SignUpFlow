"""Test validation logic."""

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from roster_cli.core.schema_validators import ValidationError, validate_workspace
from roster_cli.main import app

runner = CliRunner()


@pytest.fixture
def cricket_workspace(tmp_path: Path) -> Path:
    """Create cricket workspace."""
    workspace = tmp_path / "cricket"
    result = runner.invoke(app, ["init", "--dir", str(workspace), "--template", "cricket"])
    assert result.exit_code == 0
    return workspace


def test_validate_good_workspace(cricket_workspace: Path) -> None:
    """Test validation passes for good workspace."""
    result = runner.invoke(app, ["validate", "--dir", str(cricket_workspace)])
    assert result.exit_code == 0
    assert "Validation passed" in result.stdout


def test_validate_missing_person_ref(cricket_workspace: Path) -> None:
    """Test validation fails for missing person reference."""
    # Add invalid team member
    teams_file = cricket_workspace / "teams.yaml"
    content = teams_file.read_text()
    content = content.replace("members: [p1,", "members: [invalid_person,")
    teams_file.write_text(content)

    with pytest.raises(ValidationError) as exc_info:
        validate_workspace(cricket_workspace)

    assert "invalid_person" in str(exc_info.value)


def test_validate_invalid_event_times(cricket_workspace: Path) -> None:
    """Test validation fails for invalid event times."""
    events_file = cricket_workspace / "events.yaml"
    content = events_file.read_text()
    # Swap start and end times
    content = content.replace(
        "start: 2025-09-01T18:00:00\n    end: 2025-09-01T21:00:00",
        "start: 2025-09-01T21:00:00\n    end: 2025-09-01T18:00:00",
    )
    events_file.write_text(content)

    with pytest.raises(ValidationError) as exc_info:
        validate_workspace(cricket_workspace)

    assert "start time must be before end time" in str(exc_info.value)
