"""Validate and discover definitions before any scenario creates test data."""

from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

BUILTIN_DIRECTORY = Path(__file__).resolve().parents[2] / "docs" / "playbooks"
Identifier = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]*$")]
Role = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
Label = Annotated[str, Field(min_length=1, max_length=120, pattern=r"\S")]
Headcount = Annotated[int, Field(strict=True, ge=1)]


class PlaybookSpec(BaseModel):
    """Version 1 plugs domain data into the complete six-week roster workflow."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: Identifier
    version: Literal[1]
    workflow: Literal["six_week_roster"]
    name: Label
    event: Label
    secondary_event: Label
    critical_role: Role
    roles: dict[Role, Headcount] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_critical_role(self):
        # The absence/replacement drill removes both reserves, then adds one person.
        if self.roles.get(self.critical_role) != 1:
            raise ValueError("critical_role must name a role with exactly one required slot")
        return self


def discover_playbooks(directories: list[Path]) -> list[PlaybookSpec]:
    definitions = {}
    for directory in dict.fromkeys(path.resolve() for path in directories):
        if not directory.is_dir():
            raise ValueError(f"Playbook directory does not exist: {directory}")
        paths = sorted(directory.glob("*.json"))
        if not paths:
            raise ValueError(f"No playbook definitions in {directory}")
        for path in paths:
            try:
                spec = PlaybookSpec.model_validate_json(path.read_text())
            except (ValueError, OSError) as exc:
                raise ValueError(f"Invalid playbook {path}: {exc}") from exc
            if spec.id in definitions:
                raise ValueError(f"Duplicate playbook ID {spec.id!r}: {path}")
            definitions[spec.id] = spec
    return [definitions[key] for key in sorted(definitions)]
