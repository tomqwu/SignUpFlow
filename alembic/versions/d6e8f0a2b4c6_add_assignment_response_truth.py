"""add_assignment_response_truth

Revision ID: d6e8f0a2b4c6
Revises: c5d7e9f1a3b4
Create Date: 2026-09-13 22:45:00.000000

Existing allocation status is preserved, but no historical row is promoted to
a human acknowledgement without actor, time, and commitment-revision evidence.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d6e8f0a2b4c6"
down_revision: str | Sequence[str] | None = "c5d7e9f1a3b4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("assignments") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(),
            existing_nullable=False,
            server_default="pending",
        )
        batch_op.add_column(
            sa.Column("response_status", sa.String(), nullable=False, server_default="pending")
        )
        batch_op.add_column(sa.Column("responded_by_person_id", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("responded_at", sa.DateTime(), nullable=True))
        batch_op.add_column(
            sa.Column("commitment_revision", sa.Integer(), nullable=False, server_default="1")
        )
        batch_op.add_column(sa.Column("response_revision", sa.Integer(), nullable=True))
        batch_op.create_index("idx_assignments_response_status", ["response_status"])


def downgrade() -> None:
    with op.batch_alter_table("assignments") as batch_op:
        batch_op.drop_index("idx_assignments_response_status")
        batch_op.drop_column("response_revision")
        batch_op.drop_column("commitment_revision")
        batch_op.drop_column("responded_at")
        batch_op.drop_column("responded_by_person_id")
        batch_op.drop_column("response_status")
        batch_op.alter_column(
            "status",
            existing_type=sa.String(),
            existing_nullable=False,
            server_default="confirmed",
        )
