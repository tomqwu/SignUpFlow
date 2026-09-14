"""Prove the local validation inventory and evidence runner fail closed."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from scripts.run_local_validation import (
    aggregate_counts,
    create_run_directory,
    run_tier,
    run_validation,
    validate_manifest,
)

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "tests" / "local_validation_manifest.json"


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_manifest_classifies_every_runnable_python_test_once():
    validate_manifest(_manifest(), root=ROOT)


@pytest.mark.parametrize(
    ("tier_id", "path"),
    [
        ("api", "tests/security"),
        ("api", "tests/api/test_domain_playbooks.py"),
        ("e2e", "tests/e2e/test_domain_playbooks.py"),
    ],
)
def test_manifest_rejects_omitted_security_or_playbook_coverage(tier_id, path):
    manifest = _manifest()
    tier = next(item for item in manifest["default_tiers"] if item["id"] == tier_id)
    key = "paths" if path in tier["paths"] else "required_files"
    tier[key] = [item for item in tier[key] if item != path]

    with pytest.raises(ValueError, match="unclassified runnable tests|required coverage"):
        validate_manifest(manifest, root=ROOT)


def test_manifest_rejects_required_coverage_owned_by_the_wrong_tier():
    manifest = _manifest()
    api = next(item for item in manifest["default_tiers"] if item["id"] == "api")
    e2e = next(item for item in manifest["default_tiers"] if item["id"] == "e2e")
    path = "tests/e2e/test_domain_playbooks.py"
    e2e["required_files"].remove(path)
    api["required_files"].append(path)
    api["paths"].append(path)

    with pytest.raises(ValueError, match="wrong tier"):
        validate_manifest(manifest, root=ROOT)


def test_empty_collection_fails_and_writes_a_zero_test_receipt(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    tier = {
        "id": "empty",
        "label": "Empty",
        "paths": [str(empty)],
        "command": [sys.executable, "-m", "pytest", str(empty), "-q"],
    }

    result = run_tier(tier, artifact_dir=artifact_dir, environment={})

    assert result["status"] == "failed"
    assert result["exit_code"] == pytest.ExitCode.NO_TESTS_COLLECTED
    assert result["counts"]["tests"] == 0
    assert Path(result["artifacts"]["log"]).is_file()
    assert Path(result["artifacts"]["junit"]).is_file()


def test_zero_test_junit_cannot_pass_when_the_command_exits_zero(tmp_path, monkeypatch):
    empty_test = tmp_path / "test_empty.py"
    empty_test.write_text("# deliberately contains no tests\n")
    manifest = {
        "schema_version": 1,
        "default_tiers": [],
        "opt_in_tiers": [],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))

    tier = {
        "id": "empty",
        "label": "Empty",
        "paths": [str(empty_test)],
        "command": [
            sys.executable,
            "-c",
            (
                "import pathlib, sys; "
                "pathlib.Path(sys.argv[-1].split('=', 1)[1]).write_text("
                '\'<testsuite tests="0" failures="0" errors="0" skipped="0"/>\')'
            ),
        ],
    }
    monkeypatch.setattr(
        "scripts.run_local_validation.validate_manifest",
        lambda candidate: candidate,
    )
    monkeypatch.setattr(
        "scripts.run_local_validation.json.loads",
        lambda _content: {"default_tiers": [tier], "opt_in_tiers": []},
    )

    exit_code, report_path = run_validation(manifest_path, tmp_path / "artifacts")
    report = json.JSONDecoder().decode(report_path.read_text())

    assert exit_code == 1
    assert report["status"] == "failed"
    assert report["tiers"][0]["counts"]["tests"] == 0
    assert report["environment"]["pytest"] == pytest.__version__


def test_concurrent_runs_get_distinct_owned_artifact_directories(tmp_path):
    with ThreadPoolExecutor(max_workers=2) as executor:
        directories = list(executor.map(lambda _: create_run_directory(tmp_path), range(2)))

    assert directories[0] != directories[1]
    assert all(path.is_dir() and path.parent == tmp_path for path in directories)


def test_report_contract_includes_explicit_not_run_scopes():
    manifest = copy.deepcopy(_manifest())

    opt_in = {tier["id"]: tier for tier in manifest["opt_in_tiers"]}
    assert {"performance", "postgresql", "mobile", "providers", "artifact"} <= set(opt_in)
    assert all(tier["default_status"] == "not_run" for tier in opt_in.values())
    assert all(tier["reason"] for tier in opt_in.values())


def test_report_totals_include_only_executed_junit_counts():
    totals = aggregate_counts(
        [
            {"status": "passed", "counts": {"tests": 4, "passed": 3, "skipped": 1}},
            {"status": "not_run", "reason": "earlier failure"},
        ]
    )

    assert totals == {"tests": 4, "passed": 3, "failures": 0, "errors": 0, "skipped": 1}


def test_performance_tier_refuses_an_implicit_or_non_loopback_target():
    environment = dict(os.environ)
    environment.pop("SIGNUPFLOW_PERFORMANCE_BASE_URL", None)
    missing = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/performance/test_load.py::TestResponseTimePerformance::test_login_response_time",
            "-q",
        ],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert missing.returncode != 0
    assert "owned loopback test server" in missing.stdout + missing.stderr

    environment["SIGNUPFLOW_PERFORMANCE_BASE_URL"] = "https://example.com/api/v1"
    foreign = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/performance/test_load.py::TestResponseTimePerformance::test_login_response_time",
            "-q",
        ],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert foreign.returncode != 0
    assert "non-loopback host" in foreign.stdout + foreign.stderr
