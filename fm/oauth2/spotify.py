#!/usr/bin/env python
# encoding: utf-8

"""
fm.spotify
=========

Spotify oAuth2 Connection helper methods.
"""
import httplib

import requests
from flask import url_for
from fm.ext import config


class SpotifyOAuth2Exception(Exception):
    """ Custom Exception class to raise when errors are detected during
    the authentication flow.
    """
    pass


class SpotifyOAuth2(object):

    @staticmethod
    def get_credentials(code):
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            auth=(config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET),
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': url_for('oauth2.spotify.connect',
                                        _external=True)
            })
        if response.status_code != httplib.OK:
            raise SpotifyOAuth2Exception(response.text)
        data = response.json()
        return data['token_type'], data['access_token']

    @staticmethod
    def user_from_credentials(credentials):
        response = requests.get(
            'https://api.spotify.com/v1/me',
            headers={'authorization': '{} {}'.format(*credentials)}
        )
        if response.status_code != httplib.OK:
            raise SpotifyOAuth2Exception(response.text)
        return response.json(), credentials

    @staticmethod
    def disconnect(access_token):
        pass

    @staticmethod
    def authenticate_oauth_code(code):
        credentials = SpotifyOAuth2.get_credentials(code)
        user, credentials = SpotifyOAuth2.user_from_credentials(credentials)
        return user, credentials
