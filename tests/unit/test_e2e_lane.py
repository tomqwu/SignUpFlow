"""Keep the local Playwright command and harness wired."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e2e_local_command_present():
    makefile = (ROOT / "Makefile").read_text()
    assert "test-e2e:" in makefile
    assert "pytest tests/e2e/" in makefile
    assert "playwright install chromium" in (ROOT / "README.md").read_text()


def test_e2e_harness_committed():
    e2e = ROOT / "tests" / "e2e"
    assert (e2e / "conftest.py").exists()
    assert (e2e / "_helpers.py").exists()
    assert (e2e / "test_smoke_full_loop.py").exists()
    conf = (e2e / "conftest.py").read_text()
    assert "def live_server" in conf
    assert "sync_playwright" in conf
