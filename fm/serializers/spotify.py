#!/usr/bin/env python
# encoding: utf-8

"""
fm.serializers.spotify
======================

Kim serializers for `fm.models.spotify` models.
"""

import kim.types as t

from kim.fields import Field
from kim.contrib.sqa import SQASerializer


class ArtistSerializer(SQASerializer):
    """
    """

    id = Field(t.String, read_only=True)
    name = Field(t.String)
    spotify_uri = Field(t.String)


class AlbumSerializer(SQASerializer):
    """
    """

    id = Field(t.String, read_only=True)
    name = Field(t.String)
    spotify_uri = Field(t.String)
    images = Field(t.BaseType)

    #
    # Relations
    #

    artists = Field(t.Collection(t.Nested(ArtistSerializer)))


class TrackSerialzier(SQASerializer):
    """
    """

    id = Field(t.String, read_only=True)
    name = Field(t.String)
    duration = Field(t.Integer)
    spotify_uri = Field(t.String)
    play_count = Field(t.Integer, read_only=True)

    #
    # Relations
    #

    album = Field(t.Nested(AlbumSerializer))
