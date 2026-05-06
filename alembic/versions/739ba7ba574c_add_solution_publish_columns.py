"""add_solution_publish_columns

Revision ID: 739ba7ba574c
Revises: 7ba388eecd31
Create Date: 2026-05-06 17:10:22.735104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '739ba7ba574c'
down_revision: Union[str, Sequence[str], None] = '7ba388eecd31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('solutions', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'is_published',
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(sa.Column('published_at', sa.DateTime(), nullable=True))
        batch_op.create_index(
            'idx_solutions_org_published', ['org_id', 'is_published']
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('solutions', schema=None) as batch_op:
        batch_op.drop_index('idx_solutions_org_published')
        batch_op.drop_column('published_at')
        batch_op.drop_column('is_published')
