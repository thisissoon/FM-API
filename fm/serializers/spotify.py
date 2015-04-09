#!/usr/bin/env python
# encoding: utf-8

"""
fm.serializers.spotify
======================

Kim serializers for `fm.models.spotify` models.
"""

import kim.types as t
from fm.serializers import types
from fm.serializers.user import UserSerializer
from kim.contrib.sqa import SQASerializer
from kim.fields import Field
from kim.roles import blacklist
from kim.serializers import Serializer


class ArtistSerializer(SQASerializer):
    """
    """

    id = Field(t.String, read_only=True)
    name = Field(t.String)
    uri = Field(t.String, source='spotify_uri')


class AlbumSerializer(SQASerializer):
    """
    """

    id = Field(t.String, read_only=True)
    name = Field(t.String)
    uri = Field(t.String, source='spotify_uri')
    images = Field(t.BaseType)

    #
    # Relations
    #

    artists = Field(t.Collection(t.Nested(ArtistSerializer)))


class TrackSerializer(SQASerializer):
    """
    """

    id = Field(t.String, read_only=True)
    name = Field(t.String)
    duration = Field(t.Integer)
    uri = Field(t.String, source='spotify_uri')
    play_count = Field(t.Integer, read_only=True)

    #
    # Relations
    #

    album = Field(t.Nested(AlbumSerializer, role=blacklist('artists')))
    artists = Field(t.Collection(
        t.Nested(ArtistSerializer)),
        source='album.artists')


class HistorySerializer(SQASerializer):
    """
    """

    id = Field(t.String, read_only=True)
    track = Field(t.Nested(TrackSerializer))
    user = Field(t.Nested(UserSerializer))


class PlaylistSerializer(Serializer):
    """ Spotify playlist serializer

    Returns following data s structure:
        {
            'id': '4wtLaWQcPct5tlAWTxqjMD',
            'name': 'The Happy Hipster',
            'tracks': {
                'playlist': url to user's spotify tracks,
                'total': 186
            }
        }
    """

    class TrackSerializer(Serializer):
        """ Nested Track serializer
        Exposing url for tracks in playlist and total number of tracks in it
        """
        total = Field(t.Integer)
        playlist = Field(t.String)

    id = Field(t.String)
    name = Field(t.String)
    tracks = Field(t.Nested(TrackSerializer()))
