"""add_password_changed_at_to_person

Revision ID: cf7914ee40c0
Revises: 7ba388eecd31
Create Date: 2026-05-06 17:31:28.378854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf7914ee40c0'
down_revision: Union[str, Sequence[str], None] = '7ba388eecd31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('people', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_changed_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('people', schema=None) as batch_op:
        batch_op.drop_column('password_changed_at')
