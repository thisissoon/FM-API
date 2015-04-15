#!/usr/bin/env python
# encoding: utf-8

"""
fm.user.serializer
==================

User Kim Serializers
"""


import kim.types as t
from fm.serializers import types
from kim.fields import Field
from kim.serializers import Serializer


class UserSerializer(Serializer):
    """ Serializer for the User SQLAlchemy Model
    """

    id = Field(t.String, read_only=True)
    given_name = Field(t.String)
    family_name = Field(t.String)
    display_name = Field(t.String)
    avatar_url = Field(t.String)

    spotify_playlists = Field(types.SpotifyPlaylistEndpoint(), source='id')
