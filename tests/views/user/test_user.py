#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.user.test_user
==========================

Unit tests for the ``fm.views.user.UserView`` class.
"""

# Standard Libs
import httplib
import uuid

# Third Party Libs
import mock
from flask import url_for
from tests.factories.user import UserFactory

# First Party Libs
from fm.ext import db
from fm.serializers.user import UserSerializer


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

        response = self.client.get(url_for('users.user_spotify_playlists',
                                           user_pk=user.id))
        assert response.status_code == httplib.NO_CONTENT

    @mock.patch('fm.views.user.update_spotify_credentials')
    @mock.patch('fm.thirdparty.spotify.SpotifyApi._hit_spotify_api')
    def test_get_spotify_playlist(self, _hit_spotify_api_mock,
                                  update_spotify_credentials):
        _hit_spotify_api_mock.return_value = {
            "href": "https://api.spotify.com/v1/users/54544/playlists?of",
            "items": [
                {
                    "collaborative": False,
                    "external_urls": {
                        "spotify": "http://open.spotify.com/user/spotify/pla.."
                    },
                    "href": "https://api.spotify.com/v1/users/spotify/playl..",
                    "id": "6kxQr8LTtln4Li4dnT6N0B",
                    "images": [{
                        "height": 300,
                        "url": "https://i.scdn.co/image/1e8bde54412651f6318..",
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
                        "href": "https://api.spotify.com/v1/users/spotify/p..",
                        "total": 39
                    },
                    "type": "playlist",
                    "uri": "spotify:user:spotify:playlist:6kxQr8LTtln4Li.."
                },
                {
                    "collaborative": False,
                    "external_urls": {
                        "spotify": "http://open.spotify.com/user/spotify/pla.."
                    },
                    "href": "https://api.spotify.com/v1/users/spotify/playl..",
                    "id": "4wtLaWQcPct5tlAWTxqjMD",
                    "images": [{
                          "height": 300,
                          "url": "https://i.scdn.co/image/f005b8105b1a4db1d..",
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
                    "uri": "spotify:user:spotify:playlist:4wtLaWQcPct5gy.."
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
                'id': '6kxQr8LTtln4Li4dnT6N0B',
                'name': 'Running Motivation',
                'tracks': {
                    'playlist': url_for('users.user_spotify_track',
                                        user_pk=user.id,
                                        playlist_pk='6kxQr8LTtln4Li4dnT6N0B',
                                        _external=True),
                    'total': 39
                },
                'spotify_uri': 'spotify:user:spotify:playlist:6kxQr8LTtln4Li..'
            },
            {
                'id': '4wtLaWQcPct5tlAWTxqjMD',
                'name': 'The Happy Hipster',
                'tracks': {
                    'playlist': url_for('users.user_spotify_track',
                                        user_pk=user.id,
                                        playlist_pk='4wtLaWQcPct5tlAWTxqjMD',
                                        _external=True),
                    'total': 186
                },
                'spotify_uri': 'spotify:user:spotify:playlist:4wtLaWQcPct5gy..'
            }
        ]
        response = self.client.get(url_for('users.user_spotify_playlists',
                                           user_pk=user.id))

        assert response.status_code == httplib.OK
        assert expected == response.json

    def test_spotify_tracks_returns_204_for_unauthorized_on_spotify(self):
        user = UserFactory()
        db.session.add(user)
        db.session.commit()

        response = self.client.get(url_for('users.user_spotify_track',
                                           user_pk=user.id, playlist_pk='fda'))
        assert response.status_code == httplib.NO_CONTENT

    @mock.patch('fm.views.user.update_spotify_credentials')
    @mock.patch('fm.thirdparty.spotify.SpotifyApi._hit_spotify_api')
    def test_spotify_tracks_for_authorized_on_spotify(
            self,
            _hit_spotify_api_mock,
            update_spotify_credentials):
        user = UserFactory()

        user = UserFactory()
        user.spotify_id = '54544'

        _hit_spotify_api_mock.return_value = {
            "href": "https://api.spotify.com/v1/users/54544/playlists/..",
            "items": [
                {
                    "added_at": "2015-04-08T11:44:11Z",
                    "added_by": {
                        "external_urls": {
                            "spotify": "http://open.spotify.com/user/54544"
                        },
                        "href": "https://api.spotify.com/v1/users/54544",
                        "id": "54544",
                        "type": "user",
                        "uri": "spotify:user:54544"
                    },
                    "is_local": False,
                    "track": {
                        "album": {
                            "album_type": "album",
                            "available_markets": [],
                            "external_urls": {
                                "spotify": "https://open.spotify.com/album/6.."
                            },
                            "href": "https://api.spotify.com/v1/albums/63Tn..",
                            "id": "63Tn875CPFiwSpdKafhnvi",
                            "images": [
                                {
                                    "height": 640,
                                    "url": "https://i.scdn.co/image/23241d9..",
                                    "width": 640
                                },
                                {
                                    "height": 300,
                                    "url": "https://i.scdn.co/image/0ab35e3..",
                                    "width": 300
                                },
                                {
                                    "height": 64,
                                    "url": "https://i.scdn.co/image/8f61af0..",
                                    "width": 64
                                }
                            ],
                            "name": "Ludwig Van Beethoven: Orchestral Magni..",
                            "type": "album",
                            "uri": "spotify:album:63Tn875CPFiwSpdKafhnvi"
                        },
                        "artists": [
                            {
                                "external_urls": {
                                    "spotify": "https://open.spotify.com/art.."
                                },
                                "href": "https://api.spotify.com/v1/artists..",
                                "id": "2wOqMjp9TyABvtHdOSOTUS",
                                "name": "Ludwig van Beethoven",
                                "type": "artist",
                                "uri": "spotify:artist:2wOqMjp9TyABvtHdOSOTUS"
                            },
                            {
                                "external_urls": {
                                    "spotify": "https://open.spotify.com/art.."
                                },
                                "href": "https://api.spotify.com/v1/artists..",
                                "id": "0K23lQ2hSQAlxSEeZ05bjI",
                                "name": "Boston Symphony Orchestra",
                                "type": "artist",
                                "uri": "spotify:artist:0K23lQ2hSQAlxSEeZ05bjI"
                            },
                            {
                                "external_urls": {
                                    "spotify": "https://open.spotify.com/art.."
                                },
                                "href": "https://api.spotify.com/v1/artists..",
                                "id": "2RKnompMfdeZsyis6Gs4ce",
                                "name": "Charles Munch",
                                "type": "artist",
                                "uri": "spotify:artist:2RKnompMfdeZsyis6Gs4ce"
                            }
                        ],
                        "available_markets": [],
                        "disc_number": 1,
                        "duration_ms": 361320,
                        "explicit": False,
                        "external_ids": {
                            "isrc": "US6R21427858"
                        },
                        "external_urls": {
                            "spotify": "https://open.spotify.com/track/2zhkr.."
                        },
                        "href": "https://api.spotify.com/v1/tracks/2zhkrmXq..",
                        "id": "2zhkrmXqlGP8BXJDoBiWts",
                        "name": "Symphony No. 5 in C Minor, Op. 67: I. Alle..",
                        "popularity": 49,
                        "preview_url": "https://p.scdn.co/mp3-preview/81974..",
                        "track_number": 1,
                        "type": "track",
                        "uri": "spotify:track:2zhkrmXqlGP8BXJDoBiWts"
                    }
                },
                {
                    "added_at": "2015-04-08T11:44:18Z",
                    "added_by": {
                        "external_urls": {
                            "spotify": "http://open.spotify.com/user/54544"
                        },
                        "href": "https://api.spotify.com/v1/users/54544",
                        "id": "54544",
                        "type": "user",
                        "uri": "spotify:user:54544"
                    },
                    "is_local": False,
                    "track": {
                        "album": {
                            "album_type": "album",
                            "available_markets": [],
                            "external_urls": {
                                "spotify": "https://open.spotify.com/album/7.."
                            },
                            "href": "https://api.spotify.com/v1/albums/7oyz4..",
                            "id": "7oyz4rAEXqVz99kmWe3ejU",
                            "images": [
                                {
                                    "height": 640,
                                    "url": "https://i.scdn.co/image/8263002..",
                                    "width": 640
                                },
                                {
                                    "height": 300,
                                    "url": "https://i.scdn.co/image/f1836c8..",
                                    "width": 300
                                },
                                {
                                    "height": 64,
                                    "url": "https://i.scdn.co/image/9299ad1..",
                                    "width": 64
                                }
                            ],
                            "name": "50 Film Classics",
                            "type": "album",
                            "uri": "spotify:album:7oyz4rAEXqVz99kmWe3ejU"
                        },
                        "artists": [
                            {
                                "external_urls": {
                                    "spotify": "https://open.spotify.com/art.."
                                },
                                "href": "https://api.spotify.com/v1/artists..",
                                "id": "2uuAaf6yCHYDZDVCdMUlA3",
                                "name": "Klaus Tennstedt",
                                "type": "artist",
                                "uri": "spotify:artist:2uuAaf6yCHYDZDVCdMUlA3"
                            },
                            {
                                "external_urls": {
                                    "spotify": "https://open.spotify.com/art.."
                                },
                                "href": "https://api.spotify.com/v1/artist/..",
                                "id": "3PfJE6ebCbCHeuqO4BfNeA",
                                "name": "London Philharmonic Orchestra",
                                "type": "artist",
                                "uri": "spotify:artist:3PfJE6ebCbCHeuqO4BfNeA"
                            }
                        ],
                        "available_markets": [],
                        "disc_number": 1,
                        "duration_ms": 106853,
                        "explicit": False,
                        "external_ids": {
                            "isrc": "GBAYC8902007"
                        },
                        "external_urls": {
                            "spotify": "https://open.spotify.com/track/7rNIs.."
                        },
                        "href": "https://api.spotify.com/v1/tracks/7rNIsIG0..",
                        "id": "7rNIsIG00EuyZZzLrVDNvg",
                        "name": "Strauss, R: Also sprach Zarathustra, Op. 3..",
                        "popularity": 40,
                        "preview_url": None,
                        "track_number": 1,
                        "type": "track",
                        "uri": "spotify:track:7rNIsIG00EuyZZzLrVDNvg"
                    }
                }
            ],
            "limit": 2,
            "next": None,
            "offset": 0,
            "previous": None,
            "total": 6
        }

        expected = [{
            "album": {
                "id": "63Tn875CPFiwSpdKafhnvi",
                "spotify_uri": "spotify:album:63Tn875CPFiwSpdKafhnvi",
                "name": "Ludwig Van Beethoven: Orchestral Magni.."
            },
            "name": "Symphony No. 5 in C Minor, Op. 67: I. Alle..",
            "spotify_uri": "spotify:track:2zhkrmXqlGP8BXJDoBiWts",
            "artists": [
                {
                    "id": "2wOqMjp9TyABvtHdOSOTUS",
                    "spotify_uri": "spotify:artist:2wOqMjp9TyABvtHdOSOTUS",
                    "name": "Ludwig van Beethoven"
                }, {
                    "id": "0K23lQ2hSQAlxSEeZ05bjI",
                    "spotify_uri": "spotify:artist:0K23lQ2hSQAlxSEeZ05bjI",
                    "name": "Boston Symphony Orchestra"
                }, {
                    "id": "2RKnompMfdeZsyis6Gs4ce",
                    "spotify_uri": "spotify:artist:2RKnompMfdeZsyis6Gs4ce",
                    "name": "Charles Munch"
                }
            ],
            "duration": 361320,
            "id": "2zhkrmXqlGP8BXJDoBiWts"
        }, {
            "album": {
                "id": "7oyz4rAEXqVz99kmWe3ejU",
                "spotify_uri": "spotify:album:7oyz4rAEXqVz99kmWe3ejU",
                "name": "50 Film Classics"
            },
            "name": "Strauss, R: Also sprach Zarathustra, Op. 3..",
            "spotify_uri": "spotify:track:7rNIsIG00EuyZZzLrVDNvg",
            "artists": [
                {
                    "id": "2uuAaf6yCHYDZDVCdMUlA3",
                    "spotify_uri": "spotify:artist:2uuAaf6yCHYDZDVCdMUlA3",
                    "name": "Klaus Tennstedt"
                }, {
                    "id": "3PfJE6ebCbCHeuqO4BfNeA",
                    "spotify_uri": "spotify:artist:3PfJE6ebCbCHeuqO4BfNeA",
                    "name": "London Philharmonic Orchestra"
                }
            ],
            "duration": 106853,
            "id": "7rNIsIG00EuyZZzLrVDNvg"
        }]

        db.session.add(user)
        db.session.commit()

        response = self.client.get(url_for('users.user_spotify_track',
                                           user_pk=user.id,
                                           playlist_pk='1kYVX1rNl6nbQIOihHzP'))
        assert response.status_code == httplib.OK
        assert expected == response.json
