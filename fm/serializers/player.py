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
        """ Validates the URI to ensure the track is valid and can be played
        in the GB region.

        Arguments
        ---------
        uri : str
            The spotify track URI
        """

        spotify = spotipy.Spotify()

        try:
            self.track = spotify.track(uri)
        except spotipy.SpotifyException:
            raise ValidationError('Invalid Spotify Track URI: {0}'.format(uri))

        if 'GB' not in self.track['available_markets']:
            raise ValidationError(
                '{0} cannot be played in the GB region'.format(self.track['name']))


class VolumeSerializer(Serializer):
    """ Validates altering the player volume.
    """

    volume = Field(t.Integer, required=True)

    def validate_volume(self, value):
        """ Validates the Volume level, must be between 0 and 100.

        Arguments
        ---------
        value : int
            The proposed volume level
        """

        if not value >= 0 and not value <= 100:
            raise ValidationError('Volume must be between 0 and 100')
