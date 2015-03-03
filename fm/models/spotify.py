#!/usr/bin/env python
# encoding: utf-8

"""
fm.models.tracks
================

Models for storing Spotify Track data.
"""

import uuid

from fm.ext import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy


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

    artist = db.relationship('Artist', backref='album_associations')
    album = db.relationship('Album', backref='artist_associations')


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

    #
    # Relations
    #

    artists = association_proxy(
        'artist_associations',
        'artist',
        creator=lambda artist: ArtistAlbumAssociation(artist=artist))


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

    #
    # Relations
    #

    album = db.relation('Album', backref='tracks')
