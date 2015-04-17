"""New Genre Model

Revision ID: de29e20a272
Revises: 1ff261e9610e
Create Date: 2015-04-17 14:49:43.388383

"""

# revision identifiers, used by Alembic.
revision = 'de29e20a272'
down_revision = '1ff261e9610e'

import fm  # noqa
import sqlalchemy as sa  # noqa

from alembic import op  # noqa
from fm.ext import db  # noqa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('genre',
    sa.Column('created', fm.db.types.UTCDateTime(), nullable=False),
    sa.Column('updated', fm.db.types.UTCDateTime(), nullable=False),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('name', sa.Unicode(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_genre_created'), 'genre', ['created'], unique=False)
    op.create_index('ix_genre_name_lower', 'genre', [sa.text(u'lower(genre.name)')], unique=True)
    op.create_index(op.f('ix_genre_updated'), 'genre', ['updated'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_genre_updated'), table_name='genre')
    op.drop_index('ix_genre_name_lower', table_name='genre')
    op.drop_index(op.f('ix_genre_created'), table_name='genre')
    op.drop_table('genre')
    ### end Alembic commands ###
