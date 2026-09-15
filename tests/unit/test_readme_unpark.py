"""Marathon P4.25 — README banners reflect honest, current status."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_mobile_readme_is_active_and_has_honest_release_boundaries():
    txt = (ROOT / "mobile" / "README.md").read_text()
    # No longer the stale "paused / no new feature work" banner.
    assert "feature work is paused" not in txt
    assert "no new feature work" not in txt
    assert "Active development" in txt
    assert "#191" in txt
    assert "make mobile-codegen-check" in txt
    assert "Real iOS/Android devices | Not run" in txt
    assert "TestFlight, Play, and live backend | Not run" in txt


def test_root_readme_mentions_mobile():
    txt = (ROOT / "README.md").read_text()
    assert "Flutter mobile app" in txt
