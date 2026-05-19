"""Marathon P4.24 — the Flutter CI workflow stays wired."""

from __future__ import annotations

from pathlib import Path

WF = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "mobile-ci.yml"


def test_mobile_ci_workflow_present_and_sane():
    assert WF.exists(), "mobile-ci.yml workflow missing"
    txt = WF.read_text()
    assert "flutter pub get" in txt
    # Info-level lints must not fail the build (9 known infos in mobile/).
    assert "flutter analyze --no-fatal-infos" in txt
    assert "flutter test" in txt
    # Path-filtered so it doesn't block backend/web-only PRs.
    assert "mobile/**" in txt
