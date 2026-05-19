"""Overnight A — the blocking e2e lane + harness stay wired."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e2e_ci_job_present():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert "e2e:" in ci, "e2e CI job missing"
    assert "pytest tests/e2e/" in ci
    assert "playwright install --with-deps chromium" in ci


def test_e2e_harness_committed():
    e2e = ROOT / "tests" / "e2e"
    assert (e2e / "conftest.py").exists()
    assert (e2e / "_helpers.py").exists()
    assert (e2e / "test_smoke_full_loop.py").exists()
    conf = (e2e / "conftest.py").read_text()
    assert "def live_server" in conf
    assert "sync_playwright" in conf
