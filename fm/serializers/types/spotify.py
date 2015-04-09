import kim.types as t
import requests

from kim.exceptions import ValidationError
from simplejson import JSONDecodeError


class SpotifyURI(t.String):

    track = None

    def marshal_value(self, value):
        return self.track

    def validate(self, value):
        try:
            id = value.split(':')[-1:][0]
        except IndexError:
            raise ValidationError('Invalid Spotify URI: {0}'.format(value))

        endpoint = 'https://api.spotify.com/v1/tracks/{0}'.format(id)

        try:
            response = requests.get(endpoint)
        except requests.ConnectionError:
            raise ValidationError('Unable to get track data from Spotify')

        if not response.status_code == 200:
            raise ValidationError('Invalid Spotify Track ID: {0}'.format(id))

        try:
            track = response.json()
        except JSONDecodeError:
            raise ValidationError('Unable to read Spotify Data')

        if 'GB' not in track['available_markets']:
            raise ValidationError(
                '{0} cannot be played in the GB region'.format(track['name']))

        self.track = track
