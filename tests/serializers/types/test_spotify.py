#!/usr/bin/env python
# encoding: utf-8

"""
tests.serializers.types.test_spotify
====================================

Unit tests for sptoify Serializer field types.
"""

# Standard Libs
import httplib

# Third Party Libs
import mock
import pytest
import requests
from kim.exceptions import ValidationError
from simplejson import JSONDecodeError
from tests import TRACK_DATA

# First Party Libs
from fm.serializers.types.spotify import SpotifyURI


class TestSpotifyURI(object):

    def setup(self):
        # Patch Requests to Spotify
        self.requests = mock.MagicMock()
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(return_value=TRACK_DATA))
        self.requests.post.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(return_value={
                'access_token': 'foo',
                'expire_in': 1,
            }))
        self.requests.ConnectionError = requests.ConnectionError
        patch = mock.patch(
            'fm.serializers.types.spotify.requests',
            new_callable=mock.PropertyMock(return_value=self.requests))
        patch.start()
        self.addPatchCleanup(patch)
        patch = mock.patch(
            'fm.views.spotify.requests',
            new_callable=mock.PropertyMock(return_value=self.requests))
        patch.start()
        self.addPatchCleanup(patch)

    def should_catch_connection_error(self):
        self.requests.get.side_effect = requests.ConnectionError()

        field = SpotifyURI()

        with pytest.raises(ValidationError) as e:
            field.validate('spotify:track:foo')

        assert e.value.message == 'Unable to get track data from Spotify'

    def should_raise_error_track_not_found(self):
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.NOT_FOUND)

        field = SpotifyURI()

        with pytest.raises(ValidationError) as e:
            field.validate('spotify:track:foo')

        assert e.value.message == 'Track not found on Spotify: spotify:track:foo'

    def should_raise_error_invalid_json(self):
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(side_effect=JSONDecodeError('foo', 'bar', 0)))

        field = SpotifyURI()

        with pytest.raises(ValidationError) as e:
            field.validate('spotify:track:foo')

        assert e.value.message == 'Unable to read Spotify Data'

    def should_be_within_the_uk_region(self):
        data = TRACK_DATA.copy()
        data['available_markets'] = ['US']
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(return_value=data))

        field = SpotifyURI()

        with pytest.raises(ValidationError) as e:
            field.validate('spotify:track:foo')

        assert e.value.message == '{0} cannot be played in the GB region'.format(
            TRACK_DATA['name'])
