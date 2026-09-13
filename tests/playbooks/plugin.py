"""Pytest integration: automatic discovery, selection, fixtures and test IDs."""

from pathlib import Path
from typing import cast

import pytest

from tests.playbooks.coverage import (
    COVERAGE_MANIFEST_PATH,
    CoverageManifest,
    load_coverage_manifest,
)
from tests.playbooks.registry import BUILTIN_DIRECTORY, PlaybookSpec, discover_playbooks

_SPECS = pytest.StashKey[list[PlaybookSpec]]()
_COVERAGE = pytest.StashKey[CoverageManifest]()


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("playbooks")
    group.addoption(
        "--playbook",
        action="append",
        default=[],
        metavar="ID",
        help="Run selected playbook IDs (repeatable); default: all discovered IDs",
    )
    group.addoption(
        "--playbook-dir",
        action="append",
        default=[],
        metavar="PATH",
        help="Add a directory of JSON playbooks (repeatable)",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "playbook: data-driven operational acceptance workflow")
    directories = [BUILTIN_DIRECTORY, *(Path(p) for p in config.getoption("--playbook-dir"))]
    try:
        bundled_specs = discover_playbooks([BUILTIN_DIRECTORY])
        config.stash[_COVERAGE] = load_coverage_manifest(COVERAGE_MANIFEST_PATH, bundled_specs)
        specs = discover_playbooks(directories)
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc
    selected = set(config.getoption("--playbook"))
    unknown = selected - {spec.id for spec in specs}
    if unknown:
        raise pytest.UsageError(f"Unknown playbook IDs: {', '.join(sorted(unknown))}")
    config.stash[_SPECS] = [spec for spec in specs if not selected or spec.id in selected]


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "playbook_spec" in metafunc.fixturenames:
        metafunc.parametrize(
            "playbook_spec",
            [
                pytest.param(spec, id=spec.id, marks=pytest.mark.playbook)
                for spec in metafunc.config.stash[_SPECS]
            ],
            indirect=True,
        )


@pytest.fixture
def playbook_spec(request: pytest.FixtureRequest) -> PlaybookSpec:
    """Fresh definition per test; scenario runners must not share mutable state."""
    spec = cast(PlaybookSpec, request.param)
    return spec.model_copy(deep=True)
