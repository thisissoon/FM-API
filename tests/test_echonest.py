#!/usr/bin/env python
# encoding: utf-8

"""
tests.test_echonest
===================

Unittests for Echonest API communication functions.
"""

# Standard Libs
import httplib

# Third Party Libs
import mock
import pytest
import requests
from simplejson import JSONDecodeError
from tests import ECHONEST_ARTIST_GENRES, ECHONEST_TRACK_ANALYSIS

# First Party Libs
from fm.thirdparty.echonest import EchoNestError, get_artist_genres, get_track_analysis


class TestGetArtistGenres(object):

    def setup(self):
        # Patch Requests to EchoNest
        self.requests = mock.MagicMock()
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(return_value=ECHONEST_ARTIST_GENRES))
        self.requests.ConnectionError = requests.ConnectionError

        patch = mock.patch(
            'fm.thirdparty.echonest.requests',
            new_callable=mock.PropertyMock(return_value=self.requests))

        patch.start()
        self.addPatchCleanup(patch)

    def should_raise_exception_on_connection_error(self):
        self.requests.get.side_effect = requests.ConnectionError()

        with pytest.raises(EchoNestError) as e:
            get_artist_genres('foo')

        assert e.value.message == 'Error connecting to the Echonest API'

    def should_raise_exception_not_200_response(self):
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.NOT_FOUND)

        with pytest.raises(EchoNestError) as e:
            get_artist_genres('foo')

        assert e.value.message == 'Echonest API response code was 404 not 200'

    def should_raise_exception_on_json_decode_error(self):
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(side_effect=JSONDecodeError('foo', 'bar', 0)))

        with pytest.raises(EchoNestError) as e:
            get_artist_genres('foo')

        assert e.value.message == 'Unable to decode response data to dict'

    def should_raise_exception_no_genres(self):
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(return_value={}))

        with pytest.raises(EchoNestError) as e:
            get_artist_genres('foo')

        assert e.value.message == 'Response payload does not contain response element'

    def should_return_list_of_genres(self):
        genres = get_artist_genres('foo')

        assert type(genres) == list
        assert 'dancehall' in genres
        assert 'reggae fusion' in genres


class TestGetTrackAnalysis(object):

    def setup(self):
        # Patch Requests to EchoNest
        self.requests = mock.MagicMock()
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(return_value=ECHONEST_TRACK_ANALYSIS))
        self.requests.ConnectionError = requests.ConnectionError

        patch = mock.patch(
            'fm.thirdparty.echonest.requests',
            new_callable=mock.PropertyMock(return_value=self.requests))

        patch.start()
        self.addPatchCleanup(patch)

    def should_raise_exception_on_connection_error(self):
        self.requests.get.side_effect = requests.ConnectionError()

        with pytest.raises(EchoNestError) as e:
            get_track_analysis('foo')

        assert e.value.message == 'Error connecting to the Echonest API'

    def should_raise_exception_not_200_response(self):
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.NOT_FOUND)

        with pytest.raises(EchoNestError) as e:
            get_track_analysis('foo')

        assert e.value.message == 'Echonest API response code was 404 not 200'

    def should_raise_exception_on_json_decode_error(self):
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(side_effect=JSONDecodeError('foo', 'bar', 0)))

        with pytest.raises(EchoNestError) as e:
            get_track_analysis('foo')

        assert e.value.message == 'Unable to decode response data to dict'

    def should_raise_exception_no_summary(self):
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(return_value={}))

        with pytest.raises(EchoNestError) as e:
            get_track_analysis('foo')

        assert e.value.message == 'Response payload does not contain response element'

    def should_return_audio_summary(self):
        analysis = get_track_analysis('foo')

        assert type(analysis) == dict
        assert analysis['danceability'] == 0.5164314670162907
