"""Marathon P3.21 — ops runbook covers the real deploy surface."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_runbook_documents_current_operator_contract():
    txt = (ROOT / "docs" / "RUNBOOK.md").read_text()
    for needle in (
        "alembic upgrade head",
        "/health",
        "/ready",
        "docker compose",
        "SECRET_KEY",
        "DATABASE_URL",
        "PRODUCTION_CONFIGURATION.md",
        "No scheduled backup",
        "Rollback is not yet an accepted operator procedure",
        "#268",
    ):
        assert needle in txt, f"RUNBOOK missing: {needle}"

    assert "pg_dump" not in txt
    assert "alembic downgrade -1" not in txt
