"""Mobile validation stays local and retains the test command."""

from __future__ import annotations

from pathlib import Path

WF = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "mobile-ci.yml"


def test_mobile_validation_is_local():
    assert not WF.exists(), "Mobile CI must not be restored"
    txt = (WF.parents[2] / "mobile/README.md").read_text()
    assert "flutter pub get" in txt
    # Info-level lints must not fail the build (9 known infos in mobile/).
    assert "flutter analyze --no-fatal-infos" in txt
    assert "flutter test" in txt
    assert "$(FLUTTER) test" in (WF.parents[2] / "Makefile").read_text()
    assert "no CI checks" in txt
