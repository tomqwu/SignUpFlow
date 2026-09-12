"""Keep web coverage available locally after removing hosted test execution."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_local_commands_include_web_suite():
    txt = (ROOT / "Makefile").read_text()
    assert "pytest tests/web/" in txt
    for lane in ("tests/unit/", "tests/api/", "tests/contract/"):
        assert f"pytest {lane}" in txt
