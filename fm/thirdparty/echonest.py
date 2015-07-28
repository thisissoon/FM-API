#!/usr/bin/env python
# encoding: utf-8

"""
fm.thirdparty.echonest
======================

Echo Nest Functions for retrieving data from Echo Nest API.
"""

# Standard Libs
import httplib

# Third Party Libs
import requests
from furl import furl
from simplejson import JSONDecodeError

# First Party Libs
from fm.ext import config


BASE_URL = furl('https://developer.echonest.com').add(path=['api', 'v4']).url


class EchoNestError(Exception):
    """ Custom Echonest Exception to be raised when errors talking to the
    Echonest API occure.
    """

    pass


def get_artist_genres(uri):
    """ Retrieves a Spotify Artists Genres from Echo Nest.

    Arguments
    --------
    uri: str
        The artist spotify URI

    Returns
    -------
    list
        List of genre names
    """

    url = furl(BASE_URL) \
        .add(path=['artist', 'profile']) \
        .add({
            'api_key': config.ECHONEST_API_KEY,
            'format': 'json',
            'id': uri,
            'bucket': 'genre'
        }).url

    try:
        response = requests.get(url)
    except requests.ConnectionError:
        raise EchoNestError('Error connecting to the Echonest API')

    if not response.status_code == httplib.OK:
        raise EchoNestError(
            'Echonest API response code was {0} not 200'.format(response.status_code)
        )

    try:
        data = response.json()
    except JSONDecodeError:
        raise EchoNestError('Unable to decode response data to dict')

    try:
        genres = data['response']['artist']['genres']
    except KeyError as e:
        raise EchoNestError(
            'Response payload does not contain {0} element'.format(e.message)
        )

    return [genre['name'] for genre in genres]


def get_track_analysis(uri):
    """ Retrieves a Spotify Tracks audio profile from Echo Nest.

    Arguments
    --------
    uri: str
        The track spotify URI

    Returns
    -------
    dict
        Track audio summary
    """

    url = furl(BASE_URL) \
        .add(path=['track', 'profile']) \
        .add({
            'api_key': config.ECHONEST_API_KEY,
            'format': 'json',
            'id': uri,
            'bucket': 'audio_summary'
        }).url

    try:
        response = requests.get(url)
    except requests.ConnectionError:
        raise EchoNestError('Error connecting to the Echonest API')

    if not response.status_code == httplib.OK:
        raise EchoNestError(
            'Echonest API response code was {0} not 200'.format(response.status_code)
        )

    try:
        data = response.json()
    except JSONDecodeError:
        raise EchoNestError('Unable to decode response data to dict')

    try:
        analysis = data['response']['track']['audio_summary']
    except KeyError as e:
        raise EchoNestError(
            'Response payload does not contain {0} element'.format(e.message)
        )

    return analysis
