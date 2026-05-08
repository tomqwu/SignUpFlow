"""add_password_reset_tokens_table

Revision ID: b4e6f8a2c5d3
Revises: cf7914ee40c0
Create Date: 2026-05-08 16:55:00.000000

Replaces the in-memory reset_tokens dict in api/routers/password_reset.py
with a DB-backed table so reset links survive multi-worker deployments.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b4e6f8a2c5d3"
down_revision: str | Sequence[str] | None = "cf7914ee40c0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "password_reset_tokens",
        # Stores SHA-256 digest of the emailed token, not the raw token.
        sa.Column("token_hash", sa.String(), primary_key=True),
        sa.Column(
            "person_id",
            sa.String(),
            sa.ForeignKey("people.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "idx_password_reset_tokens_person_id",
        "password_reset_tokens",
        ["person_id"],
    )
    op.create_index(
        "idx_password_reset_tokens_expires_at",
        "password_reset_tokens",
        ["expires_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_password_reset_tokens_expires_at",
        table_name="password_reset_tokens",
    )
    op.drop_index(
        "idx_password_reset_tokens_person_id",
        table_name="password_reset_tokens",
    )
    op.drop_table("password_reset_tokens")
