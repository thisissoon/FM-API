"""empty message

Revision ID: 2e6cd97c0e82
Revises: f5babb123eb
Create Date: 2016-03-23 17:59:38.673371

"""

# revision identifiers, used by Alembic.
revision = '2e6cd97c0e82'
down_revision = 'f5babb123eb'

import fm  # noqa
import sqlalchemy as sa  # noqa

from alembic import op  # noqa
from fm.ext import db  # noqa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artist_track',
    sa.Column('created', fm.db.types.UTCDateTime(), nullable=False),
    sa.Column('updated', fm.db.types.UTCDateTime(), nullable=False),
    sa.Column('artist_id', postgresql.UUID(), nullable=False),
    sa.Column('track_id', postgresql.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['track_id'], ['track.id'], ),
    sa.PrimaryKeyConstraint('artist_id', 'track_id'),
    sa.UniqueConstraint('artist_id', 'track_id')
    )
    op.create_index(op.f('ix_artist_track_artist_id'), 'artist_track', ['artist_id'], unique=False)
    op.create_index(op.f('ix_artist_track_created'), 'artist_track', ['created'], unique=False)
    op.create_index(op.f('ix_artist_track_track_id'), 'artist_track', ['track_id'], unique=False)
    op.create_index(op.f('ix_artist_track_updated'), 'artist_track', ['updated'], unique=False)
    op.drop_table('track_artist')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('track_artist',
    sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('artist_id', postgresql.UUID(), autoincrement=False, nullable=False),
    sa.Column('track_id', postgresql.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], [u'artist.id'], name=u'track_artist_artist_id_fkey'),
    sa.ForeignKeyConstraint(['track_id'], [u'track.id'], name=u'track_artist_track_id_fkey'),
    sa.PrimaryKeyConstraint('artist_id', 'track_id', name=u'track_artist_pkey')
    )
    op.drop_index(op.f('ix_artist_track_updated'), table_name='artist_track')
    op.drop_index(op.f('ix_artist_track_track_id'), table_name='artist_track')
    op.drop_index(op.f('ix_artist_track_created'), table_name='artist_track')
    op.drop_index(op.f('ix_artist_track_artist_id'), table_name='artist_track')
    op.drop_table('artist_track')
    ### end Alembic commands ###
