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
        # TODO: Log
        return False

    if not response.status_code == httplib.OK:
        # TODO: Log
        return False

    try:
        data = response.json()
    except JSONDecodeError:
        # TODO: Log
        return False

    try:
        genres = data['response']['artist']['genres']
    except KeyError:
        # TODO: Log
        return False

    return [genre['name'] for genre in genres]
