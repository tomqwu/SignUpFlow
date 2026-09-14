"""add_solution_scope_snapshot

Revision ID: e7f9a1b3c5d7
Revises: d6e8f0a2b4c6
Create Date: 2026-09-14 01:40:00.000000

Existing solutions remain explicitly legacy. They must be regenerated before
publication because assigned rows cannot reconstruct unfilled scoped events.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e7f9a1b3c5d7"
down_revision: str | Sequence[str] | None = "d6e8f0a2b4c6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("solutions") as batch_op:
        batch_op.add_column(sa.Column("scope_start", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("scope_end", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("scope_event_ids", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("scope_fingerprint", sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("solutions") as batch_op:
        batch_op.drop_column("scope_fingerprint")
        batch_op.drop_column("scope_event_ids")
        batch_op.drop_column("scope_end")
        batch_op.drop_column("scope_start")
