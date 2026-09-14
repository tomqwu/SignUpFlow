#!/usr/bin/env python3
"""Regenerate the public Church and Basketball screenshot evidence locally."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from tests.playbooks.screenshots import (
    CAPTURE_DIRECTORY_ENV,
    CAPTURE_NOW,
    CAPTURE_SOURCE_ENV,
    finalize_capture,
    validate_manifest,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-ref", required=True, help="Full source commit SHA being captured")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    capture_root = repo_root / "docs" / "screenshots" / "current"
    manifest_path = capture_root / "manifest.json"
    if args.validate_only:
        validate_manifest(manifest_path, repo_root)
        return 0
    if len(args.source_ref) != 40:
        parser.error("--source-ref must be a full 40-character commit SHA")

    if capture_root.exists():
        shutil.rmtree(capture_root)
    capture_root.mkdir(parents=True)
    env = os.environ.copy()
    env[CAPTURE_DIRECTORY_ENV] = str(capture_root)
    env[CAPTURE_SOURCE_ENV] = args.source_ref
    env["SIGNUPFLOW_TEST_NOW"] = CAPTURE_NOW
    expression = " or ".join(
        (
            "test_domain_late_withdrawals_require_exact_available_cover",
            "test_domain_requirement_and_postponement_changes",
            "test_domain_browser_workflow",
            "test_domain_browser_rolls_published_horizon_to_week_seven",
        )
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/e2e/test_domain_playbooks.py",
            "--playbook",
            "church",
            "--playbook",
            "basketball",
            "-k",
            expression,
            "-q",
        ],
        cwd=repo_root,
        env=env,
        check=True,
    )
    manifest = finalize_capture(capture_root, repo_root, args.source_ref)
    print(f"Captured and validated {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
