"""Discovery and selection must work without editing either acceptance runner."""

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.playbooks.plugin import playbook_spec
from tests.playbooks.registry import PlaybookSpec, discover_playbooks
from tests.playbooks.runtime import Playbook

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[2]


def _definition(**changes):
    return {
        "id": "community",
        "version": 1,
        "workflow": "six_week_roster",
        "name": "Community sandbox",
        "event": "Community session",
        "secondary_event": "Preparation",
        "critical_role": "leader",
        "roles": {"leader": 1, "helper": 2},
        **changes,
    }


def test_discover_new_definition(tmp_path):
    (tmp_path / "community.json").write_text(json.dumps(_definition()))
    specs = discover_playbooks([tmp_path])
    assert [spec.id for spec in specs] == ["community"]
    assert specs[0].secondary_event == "Preparation"
    assert specs[0].late_cover_roles == []
    assert specs[0].qualification_review_role is None
    assert specs[0].extended_absence_role is None


def test_bundled_definitions_declare_domain_late_cover_roles():
    specs = {spec.id: spec for spec in discover_playbooks([ROOT / "docs" / "playbooks"])}

    assert specs["church"].late_cover_roles == ["sound", "children_leader"]
    assert specs["basketball"].late_cover_roles == ["coach", "scorekeeper"]


def test_bundled_definitions_declare_eligibility_and_availability_extensions():
    specs = {spec.id: spec for spec in discover_playbooks([ROOT / "docs" / "playbooks"])}

    assert specs["church"].qualification_review_role == "children_leader"
    assert specs["church"].extended_absence_role is None
    assert specs["basketball"].qualification_review_role is None
    assert specs["basketball"].extended_absence_role == "point_guard"


@pytest.mark.parametrize(
    "changes",
    [
        {"roles": {}},
        {"roles": {"leader": 0}},
        {"roles": {"leader": True}},
        {"roles": {"leader": "1"}},
        {"secondary_event": " "},
        {"critical_role": "missing"},
        {"late_cover_roles": ["missing"]},
        {"late_cover_roles": ["leader", "leader"]},
        {"qualification_review_role": "missing"},
        {"extended_absence_role": "missing"},
        {"roles": {"leader": 2}},
        {"version": 2},
        {"workflow": "unknown"},
        {"unexpected": True},
        {"id": "../escape"},
    ],
)
def test_reject_invalid_definitions(changes):
    with pytest.raises(ValueError):
        PlaybookSpec.model_validate(_definition(**changes))


def test_duplicate_ids_are_not_silently_overridden(tmp_path):
    for name in ("first", "second"):
        (tmp_path / f"{name}.json").write_text(json.dumps(_definition()))
    with pytest.raises(ValueError, match="Duplicate playbook"):
        discover_playbooks([tmp_path])


def test_fixture_does_not_share_mutable_roles():
    original = PlaybookSpec.model_validate(_definition())
    copied = playbook_spec.__wrapped__(SimpleNamespace(param=original))
    copied.roles["helper"] = 9
    assert original.roles["helper"] == 2


def test_unbootstrapped_runtime_cannot_seed_members():
    definition = PlaybookSpec.model_validate(_definition())
    with pytest.raises(ValueError, match="administrator"):
        Playbook(object(), definition, seed_people=True, bootstrap_admin=False)


@pytest.mark.parametrize("missing", [False, True])
def test_missing_or_empty_directory_fails(tmp_path, missing):
    path = tmp_path / "missing" if missing else tmp_path
    with pytest.raises(ValueError, match="directory|definitions"):
        discover_playbooks([path])


def test_invalid_json_reports_source(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{")
    with pytest.raises(ValueError, match="broken.json"):
        discover_playbooks([tmp_path])


def _collect(*options):
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "--color=no",
            "tests/api/test_domain_playbooks.py",
            *options,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )


def test_pytest_selects_one_bundled_playbook():
    result = _collect("--playbook", "basketball", "--playbook", "basketball")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 test collected" in result.stdout
    assert "church" not in result.stdout


def test_external_definition_plugs_into_runner(tmp_path):
    (tmp_path / "community.json").write_text(json.dumps(_definition()))
    result = _collect("--playbook-dir", str(tmp_path), "--playbook", "community")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 test collected" in result.stdout
    assert "community" in result.stdout


def test_unknown_selection_fails_instead_of_skipping():
    result = _collect("--playbook", "typo")
    assert result.returncode != 0
    assert "Unknown playbook" in result.stdout + result.stderr


def test_marker_excludes_unrelated_tests():
    result = _collect(
        "tests/unit/test_solver_role_slots.py", "-m", "playbook", "--playbook", "church"
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "test_solver_role_slots" not in result.stdout
    assert "3 deselected" in result.stdout
