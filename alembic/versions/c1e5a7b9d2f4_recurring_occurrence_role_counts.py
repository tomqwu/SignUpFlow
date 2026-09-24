"""Move recurring occurrence roles to the key the solver reads.

Occurrences generated from a recurring series stored their roles in
``extra_data.role_requirements``, but the solver, publication checks and
event helpers read only ``extra_data.role_counts``. Those occurrences were
silently unschedulable. This copies the roles across where no counts are set
and drops the stale key, so each event has one source of truth.

Revision ID: c1e5a7b9d2f4
Revises: b0d3f6a8c1e2
Create Date: 2026-09-23
"""

import json
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c1e5a7b9d2f4"
down_revision: str | None = "b0d3f6a8c1e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    connection = op.get_bind()
    rows = connection.execute(
        sa.text("SELECT id, extra_data FROM events WHERE extra_data LIKE :needle"),
        {"needle": '%"role_requirements"%'},
    ).fetchall()
    for event_id, raw in rows:
        extra = json.loads(raw)
        if not isinstance(extra, dict) or "role_requirements" not in extra:
            continue
        legacy = extra.pop("role_requirements")
        # Counts someone already set win over the series template copy.
        if legacy and not extra.get("role_counts"):
            extra["role_counts"] = legacy
        connection.execute(
            sa.text("UPDATE events SET extra_data = :extra WHERE id = :id"),
            {"extra": json.dumps(extra), "id": event_id},
        )


def downgrade() -> None:
    # Earlier code reads role_counts as well, so the moved data stays valid.
    pass
