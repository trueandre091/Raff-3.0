"""Replace scores and exp into secondary table

Revision ID: 0f23c9ee8863
Revises: 396ec505cc4f
Create Date: 2024-02-20 22:01:01.075442

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f23c9ee8863'
down_revision: Union[str, None] = '396ec505cc4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('guild_user', sa.Column('experience', sa.Integer(), nullable=True))
    op.add_column('guild_user', sa.Column('scores', sa.Integer(), nullable=True))
    op.add_column('guild_user', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('guild_user', 'updated_at')
    op.drop_column('guild_user', 'scores')
    op.drop_column('guild_user', 'experience')
    # ### end Alembic commands ###
