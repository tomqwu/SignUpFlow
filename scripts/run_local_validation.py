"""Run the declared local test tiers and emit one source-bound evidence report."""

from __future__ import annotations

import argparse
import ast
import json
import os
import platform
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "tests" / "local_validation_manifest.json"
DEFAULT_ARTIFACT_ROOT = ROOT / "test-artifacts" / "local-validation"
REQUIRED_TIER_IDS = {"unit", "api", "cli", "integration", "web", "contract", "e2e"}
REQUIRED_COVERAGE_OWNERS = {
    "tests/api/test_domain_playbooks.py": "api",
    "tests/e2e/test_domain_playbooks.py": "e2e",
    "tests/security/test_authentication.py": "api",
}


def utc_now() -> datetime:
    return datetime.now(UTC)


def create_run_directory(base: Path) -> Path:
    """Create a collision-resistant artifact directory owned by one invocation."""
    base.mkdir(parents=True, exist_ok=True)
    stamp = utc_now().strftime("%Y%m%dT%H%M%S.%fZ")
    run_dir = base / f"{stamp}-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    run_dir.mkdir()
    return run_dir


def _contains_tests(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return any(
        isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name.startswith("test_")
        for node in ast.walk(tree)
    )


def _matches_path(relative: str, declared: str) -> bool:
    return relative == declared or relative.startswith(declared.rstrip("/") + "/")


def validate_manifest(manifest: dict[str, Any], *, root: Path = ROOT) -> None:
    """Reject incomplete, overlapping, or stale test-suite declarations."""
    if manifest.get("schema_version") != 1:
        raise ValueError("unsupported local validation manifest schema")

    default_tiers = manifest.get("default_tiers", [])
    opt_in_tiers = manifest.get("opt_in_tiers", [])
    tier_ids = [tier.get("id") for tier in default_tiers]
    if set(tier_ids) != REQUIRED_TIER_IDS or len(tier_ids) != len(REQUIRED_TIER_IDS):
        raise ValueError("default tiers must declare every required local tier exactly once")

    declared_paths: list[tuple[str, str]] = []
    required_owners: dict[str, str] = {}
    for tier in default_tiers + opt_in_tiers:
        tier_id = tier.get("id")
        if not tier_id or not tier.get("label"):
            raise ValueError("every validation tier requires an id and label")
        for declared in tier.get("paths", []):
            if not (root / declared).exists():
                raise ValueError(f"validation path does not exist: {declared}")
            declared_paths.append((tier_id, declared))
        for required in tier.get("required_files", []):
            if not (root / required).is_file():
                raise ValueError(f"required coverage file does not exist: {required}")
            if required in required_owners:
                raise ValueError(f"required coverage assigned more than once: {required}")
            if not any(_matches_path(required, declared) for declared in tier.get("paths", [])):
                raise ValueError(
                    f"required coverage {required} is outside its owner tier {tier_id}"
                )
            required_owners[required] = tier_id

    missing = sorted(set(REQUIRED_COVERAGE_OWNERS) - set(required_owners))
    if missing:
        raise ValueError(f"required coverage omitted from manifest: {missing}")
    wrong_owners = {
        path: {"expected": expected, "actual": required_owners[path]}
        for path, expected in REQUIRED_COVERAGE_OWNERS.items()
        if required_owners[path] != expected
    }
    if wrong_owners:
        raise ValueError(f"required coverage assigned to wrong tier: {wrong_owners}")

    runnable = {
        str(path.relative_to(root))
        for path in (root / "tests").rglob("test*.py")
        if _contains_tests(path)
    }
    unclassified: list[str] = []
    multiply_classified: list[str] = []
    for relative in sorted(runnable):
        matches = {
            tier_id for tier_id, declared in declared_paths if _matches_path(relative, declared)
        }
        if not matches:
            unclassified.append(relative)
        elif len(matches) > 1:
            multiply_classified.append(relative)
    if unclassified:
        raise ValueError(f"unclassified runnable tests: {unclassified}")
    if multiply_classified:
        raise ValueError(f"tests assigned to multiple tiers: {multiply_classified}")

    for tier in opt_in_tiers:
        if tier.get("default_status") != "not_run" or not tier.get("reason"):
            raise ValueError(f"opt-in tier {tier['id']} needs a not_run reason")


def _junit_counts(path: Path) -> dict[str, int]:
    if not path.is_file():
        return {"tests": 0, "passed": 0, "failures": 0, "errors": 0, "skipped": 0}
    root = ElementTree.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    tests = sum(int(suite.attrib.get("tests", 0)) for suite in suites)
    failures = sum(int(suite.attrib.get("failures", 0)) for suite in suites)
    errors = sum(int(suite.attrib.get("errors", 0)) for suite in suites)
    skipped = sum(int(suite.attrib.get("skipped", 0)) for suite in suites)
    return {
        "tests": tests,
        "passed": max(0, tests - failures - errors - skipped),
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
    }


def run_tier(
    tier: dict[str, Any],
    *,
    artifact_dir: Path,
    environment: dict[str, str] | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    """Run one tier, stream its output, and return JUnit-backed evidence."""
    tier_dir = artifact_dir / tier["id"]
    tier_dir.mkdir(parents=True, exist_ok=True)
    log_path = tier_dir / "pytest.log"
    junit_path = tier_dir / "junit.xml"
    command = [*tier["command"], f"--junitxml={junit_path}"]
    started = utc_now()
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            command,
            cwd=root,
            env=os.environ.copy() if environment is None else environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            sys.stdout.write(line)
            log.write(line)
        exit_code = process.wait()
    counts = _junit_counts(junit_path)
    status = "passed" if exit_code == 0 and counts["tests"] > 0 else "failed"
    return {
        "id": tier["id"],
        "label": tier["label"],
        "status": status,
        "command": command,
        "paths": tier.get("paths", []),
        "started_at": started.isoformat().replace("+00:00", "Z"),
        "duration_seconds": round((utc_now() - started).total_seconds(), 3),
        "exit_code": exit_code,
        "counts": counts,
        "artifacts": {"log": str(log_path), "junit": str(junit_path)},
    }


def _version(command: list[str]) -> str:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    output = (result.stdout or result.stderr).strip()
    if result.returncode != 0 or not output:
        rendered = " ".join(command)
        raise RuntimeError(f"version command failed ({rendered}): {output or 'no output'}")
    return output.splitlines()[0]


def _source_sha() -> str:
    return _version(["git", "rev-parse", "HEAD"])


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def aggregate_counts(tiers: list[dict[str, Any]]) -> dict[str, int]:
    """Add JUnit counts from every executed default tier."""
    keys = ("tests", "passed", "failures", "errors", "skipped")
    return {key: sum(tier.get("counts", {}).get(key, 0) for tier in tiers) for key in keys}


def run_validation(manifest_path: Path, artifact_root: Path) -> tuple[int, Path]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    run_dir = create_run_directory(artifact_root)
    report_path = run_dir / "report.json"
    started = utc_now()
    report: dict[str, Any] = {
        "schema_version": 1,
        "source_sha": _source_sha(),
        "tracked_tree_clean": subprocess.run(
            ["git", "diff", "--quiet", "HEAD"], cwd=ROOT, check=False
        ).returncode
        == 0,
        "started_at": started.isoformat().replace("+00:00", "Z"),
        "status": "running",
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "poetry": _version(["poetry", "--version"]),
            "pytest": _version(
                [
                    "poetry",
                    "run",
                    "python",
                    "-c",
                    "import pytest; print(pytest.__version__)",
                ]
            ),
            "playwright": _version(
                [
                    "poetry",
                    "run",
                    "python",
                    "-c",
                    "import importlib.metadata; print(importlib.metadata.version('playwright'))",
                ]
            ),
        },
        "manifest": str(manifest_path),
        "artifact_directory": str(run_dir),
        "tiers": [],
        "opt_in_tiers": [
            {
                "id": tier["id"],
                "label": tier["label"],
                "status": "not_run",
                "command": tier["command"],
                "reason": tier["reason"],
            }
            for tier in manifest["opt_in_tiers"]
        ],
    }
    _write_report(report_path, report)

    exit_code = 0
    for tier in manifest["default_tiers"]:
        if exit_code:
            report["tiers"].append(
                {
                    "id": tier["id"],
                    "label": tier["label"],
                    "status": "not_run",
                    "command": tier["command"],
                    "reason": "An earlier default tier failed.",
                }
            )
        else:
            result = run_tier(tier, artifact_dir=run_dir)
            report["tiers"].append(result)
            if result["status"] == "failed":
                exit_code = result["exit_code"] or 1
        _write_report(report_path, report)

    report["status"] = "passed" if exit_code == 0 else "failed"
    report["totals"] = aggregate_counts(report["tiers"])
    report["finished_at"] = utc_now().isoformat().replace("+00:00", "Z")
    report["duration_seconds"] = round((utc_now() - started).total_seconds(), 3)
    _write_report(report_path, report)
    return exit_code, report_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    args = parser.parse_args()
    try:
        exit_code, report_path = run_validation(args.manifest, args.artifact_root)
    except (ElementTree.ParseError, OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Local validation preflight failed: {exc}", file=sys.stderr)
        return 2
    report = json.loads(report_path.read_text(encoding="utf-8"))
    totals = report["totals"]
    print(
        "Local validation totals: "
        f"{totals['passed']} passed, {totals['skipped']} skipped, "
        f"{totals['failures']} failed, {totals['errors']} errors"
    )
    print(f"Local validation report: {report_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
