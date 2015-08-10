"""spotify added into user account

Revision ID: 3a1d436efee7
Revises: 1ff261e9610e
Create Date: 2015-04-02 14:21:06.190954

"""

# revision identifiers, used by Alembic.
revision = '3a1d436efee7'
down_revision = '1ff261e9610e'
# Third Party Libs
import sqlalchemy as sa  # noqa
from alembic import op  # noqa
from sqlalchemy.dialects import postgresql

# First Party Libs
import fm  # noqa
from fm.ext import db  # noqa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('spotify_credentials', postgresql.JSON(), nullable=True))
    op.add_column('user', sa.Column('spotify_id', sa.Unicode(length=128), nullable=True))
    op.create_index(op.f('ix_user_spotify_id'), 'user', ['spotify_id'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_spotify_id'), table_name='user')
    op.drop_column('user', 'spotify_id')
    op.drop_column('user', 'spotify_credentials')
    ### end Alembic commands ###
