#!/usr/bin/env python
# encoding: utf-8

"""
fm.serializers.types.spotify
============================

Custom Kim Field Types relating to Spotifu Validation
"""

import httplib
import kim.types as t
import requests

from kim.exceptions import ValidationError
from simplejson import JSONDecodeError


class SpotifyURI(t.String):
    """ Custom field which validates a Spotify URI with the spotify API. On
    marshal the returl value will be the decoded JSON data from the Spotify
    API.
    """

    track = None

    def marshal_value(self, value):
        """ Return track data, if present, else returns None.

        Arguments
        ---------
        value : str
            The Spotiy URI

        Returns
        -------
        dict or None
            Track data from validation or None if not valid
        """

        return self.track

    def validate(self, value):
        """ Validates the value with Spotify.

        Arguments
        ---------
        value : str
            The Spotiy URI
        """

        id = value.split(':')[-1]
        endpoint = 'https://api.spotify.com/v1/tracks/{0}'.format(id)

        try:
            response = requests.get(endpoint)
        except requests.ConnectionError:
            raise ValidationError('Unable to get track data from Spotify')

        if not response.status_code == httplib.OK:
            raise ValidationError('Track not found on Spotify: {0}'.format(value))

        try:
            track = response.json()
        except JSONDecodeError:
            raise ValidationError('Unable to read Spotify Data')

        if 'GB' not in track['available_markets']:
            raise ValidationError(
                '{0} cannot be played in the GB region'.format(track['name']))

        self.track = track
