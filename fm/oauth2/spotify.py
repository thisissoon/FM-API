#!/usr/bin/env python
# encoding: utf-8

"""
fm.oauth2.spotify
=========

Spotify oAuth2 Connection helper methods.
"""
# Standard Libs
import httplib

# Third Pary Libs
import requests
from flask import url_for

# First Party Libs
from fm.ext import config


class SpotifyOAuth2Exception(Exception):
    """ Custom Exception class to raise when errors are detected during
    the authentication flow.
    """
    pass


class SpotifyOAuth2(object):

    @staticmethod
    def get_tokens(code):
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
        return response.json()

    @staticmethod
    def user_from_credentials(credentials):
        response = requests.get(
            'https://api.spotify.com/v1/me',
            headers={'authorization': '{} {}'.format(*credentials)}
        )
        if response.status_code != httplib.OK:
            raise SpotifyOAuth2Exception(response.text)
        return response.json()

    @staticmethod
    def refresh_access_token(refresh_token):
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            auth=(config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET),
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
        )
        if response.status_code != httplib.OK:
            raise SpotifyOAuth2Exception(response.text)
        return response.json()

    @staticmethod
    def disconnect(access_token):
        pass

    @staticmethod
    def authenticate_oauth_code(code):
        tokens = SpotifyOAuth2.get_tokens(code)
        credentials = (tokens['token_type'], tokens['access_token'])
        user = SpotifyOAuth2.user_from_credentials(credentials)
        return user, tokens
