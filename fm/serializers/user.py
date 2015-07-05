#!/usr/bin/env python
# encoding: utf-8

"""
fm.user.serializer
==================

User Kim Serializers
"""

# Third Party Libs
import kim.types as t
from kim.fields import Field
from kim.serializers import Serializer

# First Party Libs
from fm.serializers.types.spotify import SpotifyPlaylistEndpoint


class UserSerializer(Serializer):
    """ Serializer for the User SQLAlchemy Model
    """

    id = Field(t.String, read_only=True)
    given_name = Field(t.String)
    family_name = Field(t.String)
    display_name = Field(t.String)
    avatar_url = Field(t.String)

    spotify_playlists = Field(SpotifyPlaylistEndpoint(), source='id')
