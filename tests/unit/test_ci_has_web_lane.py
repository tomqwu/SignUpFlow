"""Marathon P3.22 — CI must run the web test suite (regression guard).

The cookie/HTMX web app grew ~190 tests across the marathon; they must
stay gated by CI, not just locally.
"""

from __future__ import annotations

from pathlib import Path

CI = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"


def test_ci_runs_web_suite():
    txt = CI.read_text()
    assert "pytest tests/web/" in txt, "CI no longer runs the web test suite"
    # Sanity: the other lanes are still present too.
    for lane in ("tests/unit/", "tests/api/", "tests/contract/"):
        assert f"pytest {lane}" in txt
