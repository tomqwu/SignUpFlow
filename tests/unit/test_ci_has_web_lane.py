"""Keep web coverage available locally after removing hosted test execution."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_local_commands_include_web_suite():
    makefile = (ROOT / "Makefile").read_text()
    manifest = json.loads((ROOT / "tests/local_validation_manifest.json").read_text())
    commands = {tier["id"]: " ".join(tier["command"]) for tier in manifest["default_tiers"]}

    assert "scripts/run_local_validation.py" in makefile
    for tier, lane in (
        ("unit", "tests/unit/"),
        ("api", "tests/api/"),
        ("web", "tests/web/"),
        ("contract", "tests/contract/"),
    ):
        assert f"pytest {lane}" in commands[tier]
