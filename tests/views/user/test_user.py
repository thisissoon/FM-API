#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.user.test_user
==========================

Unit tests for the ``fm.views.user.UserView`` class.
"""

import httplib
import uuid

import mock
from flask import url_for
from fm.ext import db
from fm.serializers.user import UserSerializer
from tests.factories.user import UserFactory


class TestUserGet(object):

    def setup(self):
        self.app.config['SPOTIFY_CLIENT_ID'] = 'cf5628'
        self.app.config['SPOTIFY_CLIENT_SECRET'] = '98db'

    def must_be_valid_uuid(self):
        url = url_for('users.user', pk='foo')
        response = self.client.get(url)

        assert response.status_code == 404

    def should_return_not_found(self):
        url = url_for('users.user', pk=unicode(uuid.uuid4()))
        response = self.client.get(url)

        assert response.status_code == 404

    def should_return_serialized_user(self):
        user = UserFactory()

        db.session.add(user)
        db.session.commit()

        url = url_for('users.user', pk=user.id)
        response = self.client.get(url)

        expected = UserSerializer().serialize(user)

        assert response.status_code == 200
        assert response.json == expected

    def test_user_has_authorized_on_spotify(self):
        user = UserFactory()
        user.spotify_id = '54774645'

        db.session.add(user)
        db.session.commit()

        url = url_for('users.user', pk=user.id)
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.json['spotify_playlists'].startswith('http')

    def test_user_has_not_authorized_on_spotify(self):
        user = UserFactory()

        db.session.add(user)
        db.session.commit()

        url = url_for('users.user', pk=user.id)
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.json['spotify_playlists'] is None

    def test_spotify_playlist_returns_204_for_unauthorized_on_spotify(self):
        user = UserFactory()
        db.session.add(user)
        db.session.commit()

        response = self.client.get(url_for('users.user_playlists', pk=user.id))
        assert response.status_code == httplib.NO_CONTENT

    @mock.patch('fm.views.user.update_spotify_credentials')
    @mock.patch('fm.thirdparty.spotify.SpotifyApi._get_user_playlist')
    def test_get_spotify_playlist(self, _get_user_playlist_mock,
                                  update_spotify_credentials):
        _get_user_playlist_mock.return_value = {
            "href": "https://api.spotify.com/v1/users/1112895716/playlists?of",
            "items": [
                {
                    "collaborative": False,
                    "external_urls": {
                        "spotify": "http://open.spotify.com/user/spotify/play/"
                    },
                    "href": "https://api.spotify.com/v1/users/spotify/playlis",
                    "id": "6kxQr8LTtln4Li4dnT6N0B",
                    "images": [{
                        "height": 300,
                        "url": "https://i.scdn.co/image/1e8bde54412651f631811",
                        "width": 300
                    }],
                    "name": "Running Motivation",
                    "owner": {
                        "external_urls": {
                            "spotify": "http://open.spotify.com/user/spotify"
                        },
                        "href": "https://api.spotify.com/v1/users/spotify",
                        "id": "spotify",
                        "type": "user",
                        "uri": "spotify:user:spotify"
                    },
                    "public": True,
                    "tracks": {
                        "href": "https://api.spotify.com/v1/users/spotify/pla",
                        "total": 39
                    },
                    "type": "playlist",
                    "uri": "spotify:user:spotify:playlist:6kxQr8LTtln4Li4dnT6N"
                },
                {
                    "collaborative": False,
                    "external_urls": {
                        "spotify": "http://open.spotify.com/user/spotify/playl"
                    },
                    "href": "https://api.spotify.com/v1/users/spotify/playlis",
                    "id": "4wtLaWQcPct5tlAWTxqjMD",
                    "images": [{
                          "height": 300,
                          "url": "https://i.scdn.co/image/f005b8105b1a4db1dbf",
                          "width": 300
                    }],
                    "name": "The Happy Hipster",
                    "owner": {
                        "external_urls": {
                            "spotify": "http://open.spotify.com/user/spotify"
                        },
                        "href": "https://api.spotify.com/v1/users/spotify",
                        "id": "spotify",
                        "type": "user",
                        "uri": "spotify:user:spotify"
                    },
                    "public": True,
                    "tracks": {
                        "href": "https://api.spotify.com/v1/users/spotify/pla",
                        "total": 186
                    },
                    "type": "playlist",
                    "uri": "spotify:user:spotify:playlist:4wtLaWQcPct5tlAWTxqj"
                }
            ],
            "limit": 3,
            "next": None,
            "offset": 0,
            "previous": None,
            "total": 6
        }

        user = UserFactory()
        user.spotify_id = '54544'
        db.session.add(user)
        db.session.commit()

        expected = [
            {
                "id": "6kxQr8LTtln4Li4dnT6N0B",
                "name": "Running Motivation"
            },
            {
                "id": "4wtLaWQcPct5tlAWTxqjMD",
                "name": "The Happy Hipster"
            }
        ]

        response = self.client.get(url_for('users.user_playlists', pk=user.id))
        assert response.status_code == httplib.OK
        assert expected == response.json
