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


def get_client_credentials():
    """Calls the spotify API to return the client credentials token
    """

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

    return r.json().get('access_token')


class SearchView(MethodView):
    """Search View.
    """

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
