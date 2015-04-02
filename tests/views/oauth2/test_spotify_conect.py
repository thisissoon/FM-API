#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.oauth2.test_google_connect
======================================

Unit tests for the ``fm.views.oauth2.GoogleConnectView`` class.
"""
import httplib
import json
import urllib

import mock
import pytest
from flask import g, url_for


class MockRequestsResponse(object):

    def __init__(self, resp_data, code=httplib.OK, msg='OK'):
        self.resp_data = resp_data
        self.code = code
        self.msg = msg
        self.headers = {'content-type': 'text/plain; charset=utf-8'}

    @property
    def text(self):
        return self.resp_data

    @property
    def status_code(self):
        return self.code

    def json(self):
        return json.loads(self.resp_data)


class TestSpotifyConnectPost(object):

    def setup(self):
        self.spotify_url = 'https://accounts.spotify.com/authorize/?' + \
            urllib.urlencode({
                'client_id': self.app.config['SPOTIFY_CLIENT_ID'],
                'response_type': 'code',
                'redirect_uri': 'https://example.com/callback',
                'state': '34fFs29kd09',
                'scope': 'user-read-private'
            })
        self.requests_get_patcher = mock.patch('requests.get')
        self.requests_get_mock = self.requests_get_patcher.start()
        self.requests_post_patcher = mock.patch('requests.post')
        self.requests_post_mock = self.requests_post_patcher.start()

    def tearDown(self):
        self.requests_get_patcher.stop()
        self.requests_post_patcher.stop()

    def test_can_spotify_oauth_url_be_resolved(self):
        assert url_for('oauth2.spotify.connect')

    @pytest.mark.usefixtures("unauthenticated")
    def test_unauthenticated_cannt_access_spotify_connect_view(self):
        response = self.client.get(url_for('oauth2.spotify.connect'))
        assert response.status_code == httplib.UNAUTHORIZED

    @pytest.mark.usefixtures("authenticated")
    def test_bla(self):
        call_back_url = url_for('oauth2.spotify.connect') + '?' + \
            urllib.urlencode({
                'code': 'callback_code',
                'state': '34fFs29kd09',
            })

        self.requests_post_mock.return_value = MockRequestsResponse(
            json.dumps({
                "access_token": "access_token",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "refresh_token"
            })
        )
        self.requests_get_mock.return_value = MockRequestsResponse(
            json.dumps({
                "country": "CZ",
                "display_name": "Test user",
                "email": "test.user@gmail.com",
                "external_urls": {
                    "spotify": "https://open.spotify.com/user/135687956"
                },
                "followers": {
                    "href": None,
                    "total": 9
                },
                "href": "https://api.spotify.com/v1/users/135687956",
                "id": "135687956",
                "images": [{
                    "height": None,
                    "url": "https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xap1/v/t1.0-1/p200x200/10325776_10152356468587453_3026104180320180669_n.jpg?oh=79534a8aee15809b01de85a90554b96c&oe=55731E30&__gda__=1436865509_df75560a7988aac0008bf4d5be2a40f4",
                    "width": None
                }],
                "product": "premium",
                "type": "user",
                "uri": "spotify:user:135687956"
            })
        )

        response = self.client.get(call_back_url)
        assert response.status_code == httplib.OK
        assert g.user.spotify_id == '135687956'
        assert g.user.spotify_credentials == ['Bearer', 'access_token', ]
