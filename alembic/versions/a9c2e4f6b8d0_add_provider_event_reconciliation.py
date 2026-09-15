"""Add provider event reconciliation state.

Revision ID: a9c2e4f6b8d0
Revises: f8a1b2c3d4e5
Create Date: 2026-09-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a9c2e4f6b8d0"
down_revision: str | None = "f8a1b2c3d4e5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("subscriptions") as batch_op:
        batch_op.add_column(sa.Column("provider_state_updated_at", sa.DateTime(), nullable=True))
        batch_op.add_column(
            sa.Column("last_provider_event_id", sa.String(length=255), nullable=True)
        )

    op.create_table(
        "provider_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("provider_event_id", sa.String(length=255), nullable=False),
        sa.Column("org_id", sa.String(), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("provider_created_at", sa.DateTime(), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_provider_events_provider_event_id",
        "provider_events",
        ["provider", "provider_event_id"],
        unique=True,
    )
    op.create_index(
        "idx_provider_events_org_created",
        "provider_events",
        ["org_id", "provider_created_at"],
    )
    op.create_index("idx_provider_events_status", "provider_events", ["status"])
    op.create_table(
        "provider_operations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("operation_key", sa.String(length=255), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("operation_type", sa.String(length=100), nullable=False),
        sa.Column("request_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("provider_object_id", sa.String(length=255), nullable=True),
        sa.Column("response_data", sa.Text(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_provider_operations_key",
        "provider_operations",
        ["provider", "operation_key"],
        unique=True,
    )
    op.create_index(
        "idx_provider_operations_org_created",
        "provider_operations",
        ["org_id", "created_at"],
    )
    op.create_index("idx_provider_operations_status", "provider_operations", ["status"])


def downgrade() -> None:
    op.drop_index("idx_provider_operations_status", table_name="provider_operations")
    op.drop_index("idx_provider_operations_org_created", table_name="provider_operations")
    op.drop_index("idx_provider_operations_key", table_name="provider_operations")
    op.drop_table("provider_operations")
    op.drop_index("idx_provider_events_status", table_name="provider_events")
    op.drop_index("idx_provider_events_org_created", table_name="provider_events")
    op.drop_index("idx_provider_events_provider_event_id", table_name="provider_events")
    op.drop_table("provider_events")

    with op.batch_alter_table("subscriptions") as batch_op:
        batch_op.drop_column("last_provider_event_id")
        batch_op.drop_column("provider_state_updated_at")
