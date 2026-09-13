"""The business-flow manifest must not silently omit roles or scenarios."""

import json
from pathlib import Path

import pytest

from tests.playbooks.coverage import (
    COVERAGE_MANIFEST_PATH,
    CoverageManifest,
    ScenarioCoverage,
    load_coverage_manifest,
)
from tests.playbooks.registry import BUILTIN_DIRECTORY, discover_playbooks

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
SHARED_IDS = {f"BO-{index:02d}" for index in range(1, 13)}


def _bundled_manifest() -> tuple[CoverageManifest, dict]:
    specs = discover_playbooks([BUILTIN_DIRECTORY])
    manifest = load_coverage_manifest(COVERAGE_MANIFEST_PATH, specs)
    return manifest, {spec.id: spec for spec in specs}


def test_manifest_covers_every_bundled_domain_role_and_required_scenario():
    manifest, specs = _bundled_manifest()

    assert {scenario.id for scenario in manifest.shared_scenarios} == SHARED_IDS
    assert set(manifest.domains) == set(specs)
    for domain_id, coverage in manifest.domains.items():
        spec = specs[domain_id]
        expected_ids = {f"{coverage.scenario_prefix}-{index:02d}" for index in range(1, 9)}
        assert {scenario.id for scenario in coverage.scenarios} == expected_ids
        assert {
            actor.qualification for actor in coverage.actors if actor.qualification is not None
        } == set(spec.roles)
        assert sum(actor.access == "admin" for actor in coverage.actors) == 1
        assert any(actor.access == "human" for actor in coverage.actors)


def test_every_manifest_row_has_an_honest_tier_and_status():
    manifest, _ = _bundled_manifest()
    scenarios = [
        *manifest.shared_scenarios,
        *(scenario for domain in manifest.domains.values() for scenario in domain.scenarios),
    ]

    for scenario in scenarios:
        assert scenario.tiers
        if scenario.status in {"automated", "partial"}:
            assert set(scenario.tiers) & {"unit", "api", "integration", "web", "e2e"}
        if scenario.status in {"manual", "blocked"}:
            assert "manual" in scenario.tiers


def test_manifest_file_evidence_resolves_in_the_repository():
    manifest, _ = _bundled_manifest()
    scenarios = [
        *manifest.shared_scenarios,
        *(scenario for domain in manifest.domains.values() for scenario in domain.scenarios),
    ]

    for scenario in scenarios:
        for evidence in scenario.evidence:
            if evidence.startswith(("tests/", "docs/")):
                assert (ROOT / evidence).is_file(), (scenario.id, evidence)


def test_partial_status_requires_executable_evidence():
    with pytest.raises(ValueError, match="executable tier"):
        ScenarioCoverage.model_validate(
            {
                "id": "BO-01",
                "actor": "administrator",
                "precondition": "An owned organization exists",
                "operation": "Run one incomplete workflow portion",
                "expected": "The implemented portion has automated evidence",
                "tiers": ["manual"],
                "status": "partial",
                "evidence": ["GitHub issue #289"],
            }
        )


def test_manifest_rejects_a_missing_shared_journey():
    data = json.loads(COVERAGE_MANIFEST_PATH.read_text())
    data["shared_scenarios"] = data["shared_scenarios"][1:]

    with pytest.raises(ValueError, match="shared scenario IDs"):
        CoverageManifest.model_validate(data)


def test_manifest_rejects_a_missing_role_actor():
    manifest, specs = _bundled_manifest()
    data = manifest.model_dump(mode="json")
    data["domains"]["church"]["actors"] = [
        actor
        for actor in data["domains"]["church"]["actors"]
        if actor.get("qualification") != "sound"
    ]

    with pytest.raises(ValueError, match="actor qualifications"):
        CoverageManifest.model_validate(data).validate_against(specs.values())


def test_manifest_rejects_a_missing_domain_scenario():
    manifest, specs = _bundled_manifest()
    data = manifest.model_dump(mode="json")
    data["domains"]["basketball"]["scenarios"] = data["domains"]["basketball"]["scenarios"][:-1]

    with pytest.raises(ValueError, match="scenario IDs"):
        CoverageManifest.model_validate(data).validate_against(specs.values())
