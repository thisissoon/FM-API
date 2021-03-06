#!/usr/bin/env python
# encoding: utf-8

"""
fm.models.tracks
================

Models for storing Spotify Track data.
"""

# Standard Libs
import uuid

# Third Party Libs
from sqlalchemy import Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr

# First Party Libs
from fm.ext import db


class Artist(db.Model):
    """ Holds Spotify Album data
    """

    __tablename__ = 'artist'

    #: Primary Key
    id = db.Column(UUID, primary_key=True, default=lambda: unicode(uuid.uuid4()))

    #: Spotify ID - spotify:artist:5nCi3BB41mBaMH9gfr6Su0
    spotify_uri = db.Column(db.Unicode(128), unique=True, nullable=False, index=True)

    #: Artist Name
    name = db.Column(db.Unicode(128))

    #
    # Relations
    #

    albums = association_proxy(
        'album_associations',
        'album',
        creator=lambda album: ArtistAlbumAssociation(album=album))

    genres = association_proxy(
        'genre_associations',
        'genre',
        creator=lambda genre: ArtistGenreAssociation(genre=genre))

    tracks = association_proxy(
        'track_associations',
        'track',
        creator=lambda track: TrackArtistAssociation(track=track))


class ArtistAlbumAssociation(db.Model):
    """ Link table joining Album to Artist
    """

    __tablename__ = 'artist_album'

    #: Artist Primary Key
    artist_id = db.Column(db.ForeignKey('artist.id'), primary_key=True, index=True)

    #: Album Primary Key
    album_id = db.Column(db.ForeignKey('album.id'), primary_key=True, index=True)

    #
    # Relations
    #

    artist = db.relationship('Artist', backref='album_associations', lazy='joined')
    album = db.relationship('Album', backref='artist_associations', lazy='joined')


class ArtistGenreAssociation(db.Model):
    """ Linking Artist to Genres
    """

    __tablename__ = 'artist_genre'

    #: Artist Primary Key
    artist_id = db.Column(db.ForeignKey('artist.id'), primary_key=True, index=True)

    #: Genre Primary Key
    grenre_id = db.Column(db.ForeignKey('genre.id'), primary_key=True, index=True)

    #
    # Relations
    #

    artist = db.relationship('Artist', backref='genre_associations', lazy='joined')
    genre = db.relationship('Genre', backref='artist_associations', lazy='joined')


class TrackArtistAssociation(db.Model):
    """ Linking Tracks to Artists
    """

    __tablename__ = 'artist_track'

    __table_args__ = (
        UniqueConstraint('artist_id', 'track_id'),
    )

    #: Artist Primary Key
    artist_id = db.Column(db.ForeignKey('artist.id'), primary_key=True, index=True)

    #: Track Primary Key
    track_id = db.Column(db.ForeignKey('track.id'), primary_key=True, index=True)

    #
    # Relations
    #

    artist = db.relationship('Artist', backref='track_associations', lazy='joined')
    track = db.relationship('Track', backref='artist_associations', lazy='joined')


class Album(db.Model):
    """ Holds Spotify Album data
    """

    __tablename__ = 'album'

    #: Primary Key
    id = db.Column(UUID, primary_key=True, default=lambda: unicode(uuid.uuid4()))

    #: Spotify ID - spotify:album:7m7F7SQ3BXvIpvOgjW51Gp
    spotify_uri = db.Column(db.Unicode(129), unique=True, nullable=False, index=True)

    #: Album Name
    name = db.Column(db.Unicode(128))

    #: Album Images - JSON object
    images = db.Column(JSON)

    #
    # Relations
    #

    artists = association_proxy(
        'artist_associations',
        'artist',
        creator=lambda artist: ArtistAlbumAssociation(artist=artist))


class Genre(db.Model):
    """ Stores Genre names from Echo Nest
    """

    __tablename__ = 'genre'

    #: Primary Key
    id = db.Column(UUID, primary_key=True, default=lambda: unicode(uuid.uuid4()))

    #: Name of the Genre
    name = db.Column(db.Unicode(128), nullable=False)

    @declared_attr
    def __table_args__(cls):
        """ Custom table arguments such as custom indexes.
        """

        return (
            Index(
                'ix_genre_name_lower',
                func.lower(cls.name),
                unique=True
            ),
        )

    #
    # Relations
    #

    artists = association_proxy(
        'artist_associations',
        'artist',
        creator=lambda artist: ArtistGenreAssociation(artist=artist))


class PlaylistHistory(db.Model):
    """ Holds the playlist history
    """

    __tablename__ = 'playlist_history'

    #: Primary Key
    id = db.Column(UUID, primary_key=True, default=lambda: unicode(uuid.uuid4()))

    #: Track ID
    track_id = db.Column(db.ForeignKey('track.id'), nullable=False, index=True)

    #: User ID
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False, index=True)

    #
    # Relations
    #

    track = db.relation('Track', lazy='joined')
    user = db.relation('User', lazy='joined')


class Track(db.Model):
    """ Holds spotify track data
    """

    __tablename__ = 'track'

    #: Primary Key
    id = db.Column(UUID, primary_key=True, default=lambda: unicode(uuid.uuid4()))

    #: Spotify ID - spotify:track:67WTwafOMgegV6ABnBQxcE
    spotify_uri = db.Column(db.Unicode(129), unique=True, nullable=False, index=True)

    #: Album ID
    album_id = db.Column(db.ForeignKey('album.id'), nullable=False, index=True)

    #: Track Name
    name = db.Column(db.Unicode(128))

    #: Duration in miliseconds
    duration = db.Column(db.Integer)

    #: Total number of times the track has been played
    play_count = db.Column(
        db.Integer,
        default=0,
        server_default='0',
        nullable=False,
        index=True)

    #: Audio analysis from Echonest
    audio_summary = db.Column(JSON)

    #
    # Relations
    #

    album = db.relation('Album', backref='tracks', lazy='joined')

    artists = association_proxy(
        'artist_associations',
        'artist',
        creator=lambda artist: TrackArtistAssociation(artist=artist))
