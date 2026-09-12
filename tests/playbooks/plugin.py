"""Pytest integration: automatic discovery, selection, fixtures and test IDs."""

from pathlib import Path

import pytest

from tests.playbooks.registry import BUILTIN_DIRECTORY, PlaybookSpec, discover_playbooks

_SPECS = pytest.StashKey[list[PlaybookSpec]]()


def pytest_addoption(parser):
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


def pytest_configure(config):
    config.addinivalue_line("markers", "playbook: data-driven operational acceptance workflow")
    directories = [BUILTIN_DIRECTORY, *(Path(p) for p in config.getoption("--playbook-dir"))]
    try:
        specs = discover_playbooks(directories)
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc
    selected = set(config.getoption("--playbook"))
    unknown = selected - {spec.id for spec in specs}
    if unknown:
        raise pytest.UsageError(f"Unknown playbook IDs: {', '.join(sorted(unknown))}")
    config.stash[_SPECS] = [spec for spec in specs if not selected or spec.id in selected]


def pytest_generate_tests(metafunc):
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
def playbook_spec(request) -> PlaybookSpec:
    """Fresh definition per test; scenario runners must not share mutable state."""
    return request.param.model_copy(deep=True)
