"""make_person_email_unique

Revision ID: c5d7e9f1a3b4
Revises: b4e6f8a2c5d3
Create Date: 2026-09-13 19:30:00.000000

Login identifies an account by email without an organization qualifier. Enforce
that invariant in the database so concurrent invitation acceptance cannot create
ambiguous accounts.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c5d7e9f1a3b4"
down_revision: str | Sequence[str] | None = "b4e6f8a2c5d3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    connection = op.get_bind()
    duplicate_emails = connection.execute(
        sa.text(
            """
            SELECT email
            FROM people
            WHERE email IS NOT NULL
            GROUP BY email
            HAVING COUNT(*) > 1
            ORDER BY email
            LIMIT 5
            """
        )
    ).scalars().all()
    if duplicate_emails:
        sample = ", ".join(duplicate_emails)
        raise RuntimeError(
            "Cannot enforce unique person emails. Resolve duplicate values first: " + sample
        )

    with op.batch_alter_table("people") as batch_op:
        batch_op.create_unique_constraint("uq_people_email", ["email"])


def downgrade() -> None:
    with op.batch_alter_table("people") as batch_op:
        batch_op.drop_constraint("uq_people_email", type_="unique")
