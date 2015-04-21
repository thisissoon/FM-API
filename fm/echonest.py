#!/usr/bin/env python
# encoding: utf-8

"""
fm.echonest
===========

Echo Nest Functions for retrieving data from Echo Nest API.
"""

import httplib

import requests
from furl import furl
from simplejson import JSONDecodeError

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

    response = requests.get(url)

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
        raise EchoNestError(e)

    return [genre['name'] for genre in genres]
