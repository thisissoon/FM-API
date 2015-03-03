#!/usr/bin/env python
# encoding: utf-8

"""
fm.serializers.player
=====================

Marshmallow schemas for player resources.
"""

import kim.types as t
import spotipy

from kim.exceptions import ValidationError
from kim.fields import Field
from kim.serializers import Serializer


class PlaylistSerializer(Serializer):
    """ This schema is used for adding tracks to the player playlist.
    """

    uri = Field(t.String, required=True)

    def validate_uri(self, uri):
        """
        """

        api = spotipy.Spotify()

        try:
            track = api.track(uri)
        except spotipy.SpotifyException:
            raise ValidationError('Invalid Spotify Track URI: {0}'.format(uri))

        if 'GB' not in track['available_markets']:
            raise ValidationError(
                '{0} cannot be played in the GB region'.format(track['name']))
