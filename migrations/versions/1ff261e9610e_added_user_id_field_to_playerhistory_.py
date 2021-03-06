"""Added user_id field to PlayerHistory model

Revision ID: 1ff261e9610e
Revises: 3da945eb68a1
Create Date: 2015-03-27 08:46:36.599337

"""

# revision identifiers, used by Alembic.
revision = '1ff261e9610e'
down_revision = '3da945eb68a1'
# Third Party Libs
import sqlalchemy as sa  # noqa
from alembic import op  # noqa
from sqlalchemy.dialects import postgresql

# First Party Libs
import fm  # noqa
from fm.ext import db  # noqa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('playlist_history', sa.Column('user_id', postgresql.UUID(), nullable=False))
    op.create_index(op.f('ix_playlist_history_user_id'), 'playlist_history', ['user_id'], unique=False)
    op.create_foreign_key(None, 'playlist_history', 'user', ['user_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'playlist_history', type_='foreignkey')
    op.drop_index(op.f('ix_playlist_history_user_id'), table_name='playlist_history')
    op.drop_column('playlist_history', 'user_id')
    ### end Alembic commands ###
