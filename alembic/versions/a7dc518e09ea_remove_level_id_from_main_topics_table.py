"""Remove level_id from main_topics table

Revision ID: a7dc518e09ea
Revises: f34b344200d4
Create Date: 2025-08-31 01:06:32.159019

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7dc518e09ea'
down_revision: Union[str, Sequence[str], None] = 'f34b344200d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite batch mode를 사용하여 level_id 컬럼 제거
    with op.batch_alter_table('main_topics', schema=None) as batch_op:
        batch_op.drop_column('level_id')


def downgrade() -> None:
    """Downgrade schema."""
    # SQLite batch mode를 사용하여 level_id 컬럼 복원
    with op.batch_alter_table('main_topics', schema=None) as batch_op:
        batch_op.add_column(sa.Column('level_id', sa.INTEGER(), nullable=False))
        batch_op.create_foreign_key(None, 'levels', ['level_id'], ['id'])
        batch_op.create_index('ix_main_topics_level_id', ['level_id'], unique=False)
