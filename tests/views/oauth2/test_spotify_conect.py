#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.oauth2.test_google_connect
======================================

Unit tests for the ``fm.views.oauth2.GoogleConnectView`` class.
"""
# Standard Libs
import httplib
import json
import urllib

# Third Pary Libs
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


@pytest.mark.usefixtures("authenticated")
class TestSpotifyConnectPost(object):

    def setup(self):
        self.app.config['SPOTIFY_CLIENT_ID'] = 'b6385af099a541188bee1e9fef4a2f'
        self.app.config['SPOTIFY_CLIENT_SECRET'] = 'b167743713c74af48051d06972'

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

    def test_add_users_spotify_credentials(self):
        call_back_url = url_for('oauth2.spotify.connect') + '?' + \
            urllib.urlencode({
                'code': 'AQD3dEZwPgjXdvDRzS3_WKMVXNYyKMNHeT1g_iHj2N9gTdT_1IQt',
                'state': '34fFs29kd09',
            })

        tokens_responce = {
            "access_token": "access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "refresh_token"
        }
        self.requests_post_mock.return_value = MockRequestsResponse(
            json.dumps(tokens_responce)
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
                    "url": "",
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
        assert g.user.spotify_credentials == tokens_responce

    def test_cannt_get_correct_credentials(self):
        call_back_url = url_for('oauth2.spotify.connect') + '?' + \
            urllib.urlencode({
                'code': 'callback_code',
                'state': '34fFs29kd09',
            })

        tokens_responce = {
            "access_token": "access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "refresh_token"
        }
        self.requests_post_mock.return_value = MockRequestsResponse(
            json.dumps(tokens_responce), code=httplib.BAD_REQUEST
        )
        response = self.client.get(call_back_url)
        assert response.status_code == httplib.UNAUTHORIZED
        assert g.user.spotify_id is None
        assert g.user.spotify_credentials is None

    def test_cannt_get_user_data(self):
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
                    "url": "",
                    "width": None
                }],
                "product": "premium",
                "type": "user",
                "uri": "spotify:user:135687956"
            }),
            code=httplib.BAD_REQUEST
        )

        response = self.client.get(call_back_url)
        assert response.status_code == httplib.UNAUTHORIZED

    def test_auth_code_is_missing(self):
        response = self.client.get(url_for('oauth2.spotify.connect'))
        assert response.status_code == httplib.BAD_REQUEST
