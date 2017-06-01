#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.spotify
================

Wraps spotify web api calls
"""

# Standard Libs
import httplib

# Third Party Libs
import requests
from flask import current_app, request
from flask.views import MethodView

# First Party Libs
from fm import http
from fm.auth import authenticated
from fm.ext import redis


def get_client_credentials():
    """Calls the spotify API to return the client credentials token
    """

    token = redis.get('fm:spotify:token')
    if token is not None:
        return token

    r = requests.post(
        'https://accounts.spotify.com/api/token',
        auth=(
            current_app.config.get('SPOTIFY_CLIENT_ID'),
            current_app.config.get('SPOTIFY_CLIENT_SECRET'),
        ),
        data={
            'grant_type': 'client_credentials',
        })

    if r.status_code != httplib.OK:
        raise Exception('invalid status code response')

    json = r.json()
    token = json.get('access_token')
    expire = json.get('expires_in')

    redis.set('fm:spotify:token', token, ex=expire)

    return token


class SearchView(MethodView):
    """Search View.
    """

    @authenticated
    def get(self):
        """Implements the search endpoint via the Spotify Web API
        which requires authentication
        """

        # TODO: exception handling
        token = get_client_credentials()

        r = requests.get(
            'https://api.spotify.com/v1/search',
            headers={
                "Authorization": "Bearer {0}".format(token),
            },
            params={
                'q': request.args.get('q'),
                'type': request.args.get('type'),
                'market': request.args.get('market'),
                'limit': request.args.get('limit'),
                'offset': request.args.get('offset'),
            })

        return http.OK(r.json())


class ArtistView(MethodView):

    @authenticated
    def get(self, id=None):
        """Returns the artist data from spotify
        """

        if id is None:
            return http.NotFound()

        # TODO: exception handling
        token = get_client_credentials()

        r = requests.get(
            'https://api.spotify.com/v1/artists/{0}'.format(id),
            headers={
                "Authorization": "Bearer {0}".format(token),
            })

        if r.status_code != httplib.OK:
            return http.NotFound()

        return http.OK(r.json())


class ArtistAlbumView(MethodView):

    @authenticated
    def get(self, id=None):
        """Returns an artists albums
        """

        if id is None:
            return http.NotFound()

        # TODO: exception handling
        token = get_client_credentials()

        r = requests.get(
            'https://api.spotify.com/v1/artists/{0}/albums'.format(id),
            headers={
                "Authorization": "Bearer {0}".format(token),
            },
            params=request.args)

        if r.status_code != httplib.OK:
            return http.NotFound()

        return http.OK(r.json())


class ArtistsTopTrackView(MethodView):

    @authenticated
    def get(self, id=None):
        """Returns an artists top tracks
        """

        if id is None:
            return http.NotFound()

        # TODO: exception handling
        token = get_client_credentials()

        r = requests.get(
            'https://api.spotify.com/v1/artists/{0}/top-tracks'.format(id),
            headers={
                "Authorization": "Bearer {0}".format(token),
            },
            params=request.args)

        if r.status_code != httplib.OK:
            return http.NotFound()

        return http.OK(r.json())


class ArtistsRelatedView(MethodView):

    @authenticated
    def get(self, id=None):
        """Returns an artists related artists
        """

        if id is None:
            return http.NotFound()

        # TODO: exception handling
        token = get_client_credentials()

        r = requests.get(
            'https://api.spotify.com/v1/artists/{0}/related-artists'.format(id),
            headers={
                "Authorization": "Bearer {0}".format(token),
            },
            params=request.args)

        if r.status_code != httplib.OK:
            return http.NotFound()

        return http.OK(r.json())


class AlbumView(MethodView):

    @authenticated
    def get(self, id=None):
        """Returns the album from spotify
        """

        if id is None:
            return http.NotFound()

        # TODO: exception handling
        token = get_client_credentials()

        r = requests.get(
            'https://api.spotify.com/v1/albums/{0}'.format(id),
            headers={
                "Authorization": "Bearer {0}".format(token),
            })

        if r.status_code != httplib.OK:
            return http.NotFound()

        return http.OK(r.json())


class AlbumTrackView(MethodView):

    @authenticated
    def get(self, id=None):
        """Returns an albums tracks
        """

        if id is None:
            return http.NotFound()

        # TODO: exception handling
        token = get_client_credentials()

        r = requests.get(
            'https://api.spotify.com/v1/albums/{0}/tracks'.format(id),
            headers={
                "Authorization": "Bearer {0}".format(token),
            },
            params=request.args)

        if r.status_code != httplib.OK:
            return http.NotFound()

        return http.OK(r.json())


class TrackView(MethodView):

    @authenticated
    def get(self, id=None):
        """Returns the track from spotify
        """

        if id is None:
            return http.NotFound()

        # TODO: exception handling
        token = get_client_credentials()

        r = requests.get(
            'https://api.spotify.com/v1/tracks/{0}'.format(id),
            headers={
                "Authorization": "Bearer {0}".format(token),
            })

        if r.status_code != httplib.OK:
            return http.NotFound()

        return http.OK(r.json())
