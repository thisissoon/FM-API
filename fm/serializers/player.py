#!/usr/bin/env python
# encoding: utf-8

"""
fm.serializers.player
=====================

Marshmallow schemas for player resources.
"""
# Third Party Libs
import kim.types as t
from kim.exceptions import ValidationError
from kim.fields import Field
from kim.serializers import Serializer

# First Party Libs
from fm.serializers.types.spotify import SpotifyURI


class PlaylistSerializer(Serializer):
    """ This schema is used for adding tracks to the player playlist.
    """

    uri = Field(SpotifyURI, required=True)


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

        if not value >= 0:
            raise ValidationError('Volume must be greater than 0')

        if not value <= 100:
            raise ValidationError('Volume must be less than 100')
