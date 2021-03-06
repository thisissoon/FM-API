"""Renaming spotify_id to spotify_uri

Revision ID: 2937e25e93cd
Revises: 219d09e1a415
Create Date: 2015-03-03 16:59:38.501727

"""

# revision identifiers, used by Alembic.
revision = '2937e25e93cd'
down_revision = '219d09e1a415'
# Third Party Libs
import sqlalchemy as sa  # noqa
from alembic import op  # noqa

# First Party Libs
import fm  # noqa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('album', sa.Column('spotify_uri', sa.Unicode(length=129), nullable=False))
    op.create_index(op.f('ix_album_spotify_uri'), 'album', ['spotify_uri'], unique=True)
    op.drop_index('ix_album_spotify_id', table_name='album')
    op.drop_column('album', 'spotify_id')
    op.add_column('artist', sa.Column('spotify_uri', sa.Unicode(length=128), nullable=False))
    op.create_index(op.f('ix_artist_spotify_uri'), 'artist', ['spotify_uri'], unique=True)
    op.drop_index('ix_artist_spotify_id', table_name='artist')
    op.drop_column('artist', 'spotify_id')
    op.add_column('track', sa.Column('spotify_uri', sa.Unicode(length=129), nullable=False))
    op.create_index(op.f('ix_track_spotify_uri'), 'track', ['spotify_uri'], unique=True)
    op.drop_index('ix_track_spotify_id', table_name='track')
    op.drop_column('track', 'spotify_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('track', sa.Column('spotify_id', sa.VARCHAR(length=129), autoincrement=False, nullable=False))
    op.create_index('ix_track_spotify_id', 'track', ['spotify_id'], unique=True)
    op.drop_index(op.f('ix_track_spotify_uri'), table_name='track')
    op.drop_column('track', 'spotify_uri')
    op.add_column('artist', sa.Column('spotify_id', sa.VARCHAR(length=128), autoincrement=False, nullable=False))
    op.create_index('ix_artist_spotify_id', 'artist', ['spotify_id'], unique=True)
    op.drop_index(op.f('ix_artist_spotify_uri'), table_name='artist')
    op.drop_column('artist', 'spotify_uri')
    op.add_column('album', sa.Column('spotify_id', sa.VARCHAR(length=129), autoincrement=False, nullable=False))
    op.create_index('ix_album_spotify_id', 'album', ['spotify_id'], unique=True)
    op.drop_index(op.f('ix_album_spotify_uri'), table_name='album')
    op.drop_column('album', 'spotify_uri')
    ### end Alembic commands ###
