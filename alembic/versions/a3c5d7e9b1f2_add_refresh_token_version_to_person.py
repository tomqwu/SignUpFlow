"""add_refresh_token_version_to_person

Sprint 9 PR 9.3 follow-up. Adds a per-user counter that is bumped on
every successful /auth/refresh so the prior refresh token becomes
unusable (replay attack prevention).

Revision ID: a3c5d7e9b1f2
Revises: cf7914ee40c0
Create Date: 2026-05-08 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3c5d7e9b1f2'
down_revision: Union[str, Sequence[str], None] = 'cf7914ee40c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('people', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'refresh_token_version',
                sa.Integer(),
                nullable=False,
                server_default='0',
            )
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('people', schema=None) as batch_op:
        batch_op.drop_column('refresh_token_version')
