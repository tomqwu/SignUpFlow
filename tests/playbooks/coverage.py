"""Machine-readable business-flow coverage and cross-playbook validation."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from tests.playbooks.registry import BUILTIN_DIRECTORY, Identifier, Label, PlaybookSpec, Role

COVERAGE_MANIFEST_PATH = BUILTIN_DIRECTORY / "coverage.json"
ScenarioId = Annotated[str, Field(pattern=r"^[A-Z]{2}-[0-9]{2}$")]
ScenarioPrefix = Annotated[str, Field(pattern=r"^[A-Z]{2}$")]
Detail = Annotated[str, Field(min_length=1, max_length=300, pattern=r"\S")]
Tier = Literal["unit", "api", "integration", "web", "e2e", "manual"]
CoverageStatus = Literal["automated", "partial", "manual", "blocked"]
Access = Literal["admin", "volunteer", "human"]


class ScenarioCoverage(BaseModel):
    """Trace one stable scenario ID to its operation, oracle, and evidence tier."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: ScenarioId
    actor: Identifier
    precondition: Detail
    operation: Detail
    expected: Detail
    tiers: list[Tier] = Field(min_length=1)
    status: CoverageStatus
    evidence: list[Detail] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_status_tiers(self) -> Self:
        executable = {"unit", "api", "integration", "web", "e2e"}
        if self.status in {"automated", "partial"} and not executable.intersection(self.tiers):
            raise ValueError("automated or partial scenarios require an executable tier")
        if self.status in {"manual", "blocked"} and "manual" not in self.tiers:
            raise ValueError("manual or blocked scenarios require the manual tier")
        return self


class ActorCoverage(BaseModel):
    """Describe one operational actor without inventing a new permission level."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: Identifier
    label: Label
    access: Access
    qualification: Role | None = None
    actions: list[Identifier] = Field(min_length=1)


class DomainCoverage(BaseModel):
    """Coverage rows owned by one bundled playbook."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    scenario_prefix: ScenarioPrefix
    actors: list[ActorCoverage] = Field(min_length=1)
    scenarios: list[ScenarioCoverage] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_rows(self) -> Self:
        actor_ids = [actor.id for actor in self.actors]
        if len(actor_ids) != len(set(actor_ids)):
            raise ValueError("actor IDs must be unique")
        scenario_ids = [scenario.id for scenario in self.scenarios]
        if len(scenario_ids) != len(set(scenario_ids)):
            raise ValueError("scenario IDs must be unique")
        expected = {f"{self.scenario_prefix}-{index:02d}" for index in range(1, 9)}
        if set(scenario_ids) != expected:
            raise ValueError(f"domain scenario IDs must be exactly {sorted(expected)}")
        if {scenario.actor for scenario in self.scenarios} - set(actor_ids):
            raise ValueError("domain scenarios must reference declared actors")
        return self


class CoverageManifest(BaseModel):
    """Required shared journeys plus role-complete bundled domain coverage."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    version: Literal[1]
    shared_scenarios: list[ScenarioCoverage] = Field(min_length=1)
    domains: dict[Identifier, DomainCoverage] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_shared_scenarios(self) -> Self:
        expected = {f"BO-{index:02d}" for index in range(1, 13)}
        actual = [scenario.id for scenario in self.shared_scenarios]
        if len(actual) != len(set(actual)) or set(actual) != expected:
            raise ValueError(f"shared scenario IDs must be exactly {sorted(expected)}")
        return self

    def validate_against(self, specs: Iterable[PlaybookSpec]) -> Self:
        """Reject omitted domains, scheduling roles, invalid prefixes, or actor references."""
        by_id = {spec.id: spec for spec in specs}
        if set(self.domains) != set(by_id):
            raise ValueError("coverage domains must match bundled playbook IDs")
        shared_actor_ids = {scenario.actor for scenario in self.shared_scenarios}
        for domain_id, domain in self.domains.items():
            spec = by_id[domain_id]
            qualifications = {
                actor.qualification for actor in domain.actors if actor.qualification is not None
            }
            if qualifications != set(spec.roles):
                raise ValueError(f"{domain_id} actor qualifications must match playbook roles")
            if sum(actor.access == "admin" for actor in domain.actors) != 1:
                raise ValueError(f"{domain_id} must declare exactly one admin actor")
            if not any(actor.access == "human" for actor in domain.actors):
                raise ValueError(f"{domain_id} must declare a human responsibility boundary")
            actor_ids = {actor.id for actor in domain.actors}
            if shared_actor_ids - actor_ids:
                raise ValueError(f"{domain_id} does not declare every shared-scenario actor")
        return self


def load_coverage_manifest(path: Path, specs: Iterable[PlaybookSpec]) -> CoverageManifest:
    """Load and cross-check the manifest before playbook tests collect."""
    try:
        manifest = CoverageManifest.model_validate_json(path.read_text())
    except (ValueError, OSError) as exc:
        raise ValueError(f"Invalid playbook coverage manifest {path}: {exc}") from exc
    return manifest.validate_against(specs)
