#!/usr/bin/env python
# encoding: utf-8

"""
fm.serializers.types.spotify
============================

Custom Kim Field Types relating to Spotifu Validation
"""

# Standard Libs
import httplib

# Third Party Libs
import requests
from flask import url_for
from kim import types as t
from kim.exceptions import ValidationError
from simplejson import JSONDecodeError

# First Party Libs
from fm.models.user import User
from fm.views.spotify import get_client_credentials


class SpotifyPlaylistEndpoint(t.String):
    """ A custom type for user's spotify playlists.
    Source must be set up for user id

    Example
    -------
        >>> Field(types.SpotifyPlaylistEndpoint(), source='id')
    """

    def serialize_value(self, value):
        user = User.query.get(value)
        if user.spotify_id is None:
            return None
        return url_for('users.user_spotify_playlists', user_pk=value,
                       _external=True)


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

        try:
            token = get_client_credentials()
        except:
            return ValidationError('Spotify credentials error')

        spotify_api_map = {
            'track': 'https://api.spotify.com/v1/tracks/{0}',
            'album': 'https://api.spotify.com/v1/albums/{0}'
        }
        try:
            _, tpe, uri = value.split(':')
            endpoint = spotify_api_map[tpe].format(uri)
        except (KeyError, ValueError):
            raise ValidationError('Unknow spotify uri: {}'.format(value))

        try:
            response = requests.get(
                endpoint,
                headers={
                    "Authorization": "Bearer {0}".format(token),
                })
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
