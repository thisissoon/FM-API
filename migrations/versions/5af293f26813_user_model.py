"""User Model

Revision ID: 5af293f26813
Revises: 8778ad8a7ab
Create Date: 2015-03-06 14:26:27.380921

"""

# revision identifiers, used by Alembic.
revision = '5af293f26813'
down_revision = '491f96ede5d0'
# Third Party Libs
import sqlalchemy as sa  # noqa
from alembic import op  # noqa
from sqlalchemy.dialects import postgresql

# First Party Libs
import fm  # noqa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('created', fm.db.types.UTCDateTime(), nullable=False),
    sa.Column('updated', fm.db.types.UTCDateTime(), nullable=False),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('gplus_id', sa.Unicode(length=128), nullable=False),
    sa.Column('token', sa.Text(), nullable=False),
    sa.Column('email', sa.Unicode(length=128), nullable=False),
    sa.Column('given_name', sa.Unicode(length=128), nullable=False),
    sa.Column('family_name', sa.Unicode(length=128), nullable=False),
    sa.Column('display_name', sa.Unicode(length=128), nullable=False),
    sa.Column('avatar_url', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_created'), 'user', ['created'], unique=False)
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=False)
    op.create_index(op.f('ix_user_gplus_id'), 'user', ['gplus_id'], unique=False)
    op.create_index(op.f('ix_user_token'), 'user', ['token'], unique=False)
    op.create_index(op.f('ix_user_updated'), 'user', ['updated'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_updated'), table_name='user')
    op.drop_index(op.f('ix_user_token'), table_name='user')
    op.drop_index(op.f('ix_user_gplus_id'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_index(op.f('ix_user_created'), table_name='user')
    op.drop_table('user')
    ### end Alembic commands ###