"""Add durable notification delivery leases.

Revision ID: b0d3f6a8c1e2
Revises: a9c2e4f6b8d0
Create Date: 2026-09-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b0d3f6a8c1e2"
down_revision: str | None = "a9c2e4f6b8d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("notifications") as batch_op:
        batch_op.add_column(
            sa.Column("delivery_attempts", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(sa.Column("delivery_lease_token", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("delivery_lease_expires_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("next_attempt_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("last_attempt_at", sa.DateTime(), nullable=True))
        batch_op.create_index(
            "idx_notifications_delivery_due",
            ["org_id", "status", "next_attempt_at"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("notifications") as batch_op:
        batch_op.drop_index("idx_notifications_delivery_due")
        batch_op.drop_column("last_attempt_at")
        batch_op.drop_column("next_attempt_at")
        batch_op.drop_column("delivery_lease_expires_at")
        batch_op.drop_column("delivery_lease_token")
        batch_op.drop_column("delivery_attempts")
