"""Marathon P3.21 — ops runbook covers the real deploy surface."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_runbook_documents_key_ops():
    txt = (ROOT / "docs" / "RUNBOOK.md").read_text()
    for needle in (
        "alembic upgrade head",
        "/health",
        "/ready",
        "docker compose",
        "SECRET_KEY",
        "pg_dump",
    ):
        assert needle in txt, f"RUNBOOK missing: {needle}"
