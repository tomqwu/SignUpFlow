"""Add durable notification delivery key.

Revision ID: f8a1b2c3d4e5
Revises: e7f9a1b3c5d7
Create Date: 2026-09-14
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "f8a1b2c3d4e5"
down_revision: str | None = "e7f9a1b3c5d7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("notifications") as batch_op:
        batch_op.add_column(sa.Column("delivery_key", sa.String(), nullable=True))
        batch_op.create_index("idx_notifications_delivery_key", ["delivery_key"], unique=True)


def downgrade() -> None:
    with op.batch_alter_table("notifications") as batch_op:
        batch_op.drop_index("idx_notifications_delivery_key")
        batch_op.drop_column("delivery_key")
