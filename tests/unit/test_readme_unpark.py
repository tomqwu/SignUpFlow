"""Marathon P4.25 — README banners reflect honest, current status."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_mobile_readme_unparked_and_honest():
    txt = (ROOT / "mobile" / "README.md").read_text()
    # No longer the stale "paused / no new feature work" banner.
    assert "feature work is paused" not in txt
    assert "no new feature work" not in txt
    # Un-parked, but the codegen gap is stated (not hidden).
    assert "Un-parked" in txt
    assert "#191" in txt
    assert "make mobile-codegen" in txt


def test_root_readme_mentions_mobile():
    txt = (ROOT / "README.md").read_text()
    assert "Flutter mobile app" in txt
