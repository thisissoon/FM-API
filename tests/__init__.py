#!/usr/bin/env python
# encoding: utf-8

"""
tests
=====

Test suite for FM Player setup.
"""
from __future__ import unicode_literals

# Standard Libs
import os


# Set Tests to user Test Config
os.environ['FM_SETTINGS_MODULE'] = 'fm.config.test'

# Example response from Spotify Track API
TRACK_DATA = {
    'album': {
        'album_type': 'album',
        'available_markets': ['GB'],
        'external_urls': {
            'spotify': 'https://open.spotify.com/album/5SpcwnEVClk33l5QM04vSy'
        },
        'href': 'https://api.spotify.com/v1/albums/5SpcwnEVClk33l5QM04vSy',
        'id': '5SpcwnEVClk33l5QM04vSy',
        'images': [
            {
                'height': 640,
                'url': 'https://i.scdn.co/image/770cfef8e832ae47139debe788f76',
                'width': 640
            }, {
                'height': 300,
                'url': 'https://i.scdn.co/image/dcb8f435712888a71f4106b1ed83d',
                'width': 300
            }, {
                'height': 64,
                'url': 'https://i.scdn.co/image/8a87ca6a9fc52e63c1c69f32d14c9',
                'width': 64
            }
        ],
        'name': 'Devotion',
        'type': 'album',
        'uri': 'spotify:album:5SpcwnEVClk33l5QM04vSy'
    },
    'artists': [
        {
            'external_urls': {
                'spotify': 'https://open.spotify.com/artist/5v61OSg53KaQxGMpEp'
            },
            'href': 'https://api.spotify.com/v1/artists/5v61OSg53KaQxGMpErkBN',
            'id': '5v61OSg53KaQxGMpErkBNp',
            'name': 'Anberlin',
            'type': 'artist',
            'uri': 'spotify:artist:5v61OSg53KaQxGMpErkBNp'
        }
    ],
    'available_markets': ['GB'],
    'disc_number': 1,
    'duration_ms': 201806,
    'explicit': False,
    'external_ids': {
        'isrc': 'USUM71210069'
    },
    'external_urls': {
        'spotify': 'https://open.spotify.com/track/11oRv2sfZJxNYqCl6wLaqJ'
    },
    'href': 'https://api.spotify.com/v1/tracks/11oRv2sfZJxNYqCl6wLaqJ',
    'id': '11oRv2sfZJxNYqCl6wLaqJ',
    'name': 'Little Tyrants',
    'popularity': 32,
    'preview_url': 'https://p.scdn.co/mp3-preview/93d539cdfc573ae899bfc57245a',
    'track_number': 2,
    'type': 'track',
    'uri': 'spotify:track:11oRv2sfZJxNYqCl6wLaqJ'
}

ALBUM_TRACKS_DATA = {
    "href": "https://api.spotify.com/v1/albums/6akEvsycLGftJxYudPjmqK/tracks",
    "items": [
        {
            "artists": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/08td7MxkoQ"
                    },
                    "href": "https://api.spotify.com/v1/artists/08td7MxkoHQkQ",
                    "id": "08td7MxkoHQkXnWAYD8d6Q",
                    "name": "TaniaBowra",
                    "type": "artist",
                    "uri": "spotify:artist:08td7MxkoHQkXnWAYD8d6Q"
                }
            ],
            "available_markets": [
                "GB"
            ],
            "disc_number": 1,
            "duration_ms": 276773,
            "explicit": False,
            "external_urls": {
                "spotify": "https://open.spotify.com/track/2TpxZ7JUBn3uw46aR7V"
            },
            "href": "https://api.spotify.com/v1/tracks/2TpxZ7JUBn3uw46aR7qd6V",
            "id": "2TpxZ7JUBn3uw46aR7qd6V",
            "name": "AllIWant",
            "preview_url": "https://p.scdn.co/mp3-preview/6d00206e32194d15df3",
            "track_number": 1,
            "type": "track",
            "uri": "spotify:track:2TpxZ7JUBn3uw46aR7qd6V"
        },
        {
            "artists": [
                {
                    "external_urls": {
                        "spotify": "https://open.spotify.com/artist/08td7Mxk6Q"
                    },
                    "href": "https://api.spotify.com/v1/artists/08td7MxkoHQkQ",
                    "id": "08td7MxkoHQkXnWAYD8d6Q",
                    "name": "TaniaBowra",
                    "type": "artist",
                    "uri": "spotify:artist:08td7MxkoHQkXnWAYD8d6Q"
                }
            ],
            "available_markets": [
                "GB"
            ],
            "disc_number": 1,
            "duration_ms": 247680,
            "explicit": False,
            "external_urls": {
                "spotify": "https://open.spotify.com/track/4PjcfyZZVE10TFd9EKr"
            },
            "href": "https://api.spotify.com/v1/tracks/4PjcfyZZVE10TFd9EKA72r",
            "id": "4PjcfyZZVE10TFd9EKA72r",
            "name": "Someday",
            "preview_url": "https://p.scdn.co/mp3-preview/2b15de922bf4f4b8cff",
            "track_number": 2,
            "type": "track",
            "uri": "spotify:track:4PjcfyZZVE10TFd9EKA72r"
        }
    ],
    "limit": 50,
    "next": None,
    "offset": 0,
    "previous": None,
    "total": 2
}


ALBUM_DATA = {
    "album_type": "album",
    "artists": [
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/08td7MxkoHQkXnWAYD"
            },
            "href": "https://api.spotify.com/v1/artists/08td7MxkoHQkXnWAYD8d6",
            "id": "08td7MxkoHQkXnWAYD8d6Q",
            "name": "Tania Bowra",
            "type": "artist",
            "uri": "spotify:artist:08td7MxkoHQkXnWAYD8d6Q"
        }
    ],
    "available_markets": [
        "GB"
    ],
    "copyrights": [
        {
            "text": "2004 Craving Records",
            "type": "C"
        },
        {
            "text": "2004 Craving Records",
            "type": "P"
        }
    ],
    "external_ids": {
        "upc": "9324690012824"
    },
    "external_urls": {
        "spotify": "https://open.spotify.com/album/6akEvsycLGftJxYudPjmqK"
    },
    "genres": [],
    "href": "https://api.spotify.com/v1/albums/6akEvsycLGftJxYudPjmqK",
    "id": "6akEvsycLGftJxYudPjmqK",
    "images": [
        {
            "height": 640,
            "url": "https://i.scdn.co/image/f2798ddab0c7b76dc2d270b65c4f67dde",
            "width": 640
        },
        {
            "height": 300,
            "url": "https://i.scdn.co/image/b414091165ea0f4172089c2fc67bb35aa",
            "width": 300
        },
        {
            "height": 64,
            "url": "https://i.scdn.co/image/8522fc78be4bf4e83fea8e67bb742e7d3",
            "width": 64
        }
    ],
    "name": "Place In The Sun",
    "popularity": 7,
    "release_date": "2004-02-02",
    "release_date_precision": "day",
    "tracks": {
        "href": "https://api.spotify.com/v1/albums/6akEvsycLGftJxYudPjmqK/tra",
        "items": [
            {
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/08td6"
                        },
                        "href": "https://api.spotify.com/v1/artists/08td7MxkQ",
                        "id": "08td7MxkoHQkXnWAYD8d6Q",
                        "name": "Tania Bowra",
                        "type": "artist",
                        "uri": "spotify:artist:08td7MxkoHQkXnWAYD8d6Q"
                    }
                ],
                "available_markets": [
                    "GB"
                ],
                "disc_number": 1,
                "duration_ms": 276773,
                "explicit": False,
                "external_urls": {
                    "spotify": "https://open.spotify.com/track/2TpxZ7JUBn3ud6V"
                },
                "href": "https://api.spotify.com/v1/tracks/2TpxZ7JUBn3uw46aRV",
                "id": "2TpxZ7JUBn3uw46aR7qd6V",
                "name": "All I Want",
                "preview_url": "https://p.scdn.co/mp3-preview/6d00206e32194d5",
                "track_number": 1,
                "type": "track",
                "uri": "spotify:track:2TpxZ7JUBn3uw46aR7qd6V"
            },
            {
                "artists": [
                    {
                        "external_urls": {
                            "spotify": "https://open.spotify.com/artist/08td6Q"
                        },
                        "href": "https://api.spotify.com/v1/artists/08td7MxkQ",
                        "id": "08td7MxkoHQkXnWAYD8d6Q",
                        "name": "Tania Bowra",
                        "type": "artist",
                        "uri": "spotify:artist:08td7MxkoHQkXnWAYD8d6Q"
                    }
                ],
                "available_markets": [
                    "GB"
                ],
                "disc_number": 1,
                "duration_ms": 247680,
                "explicit": False,
                "external_urls": {
                    "spotify": "https://open.spotify.com/track/4PjcfyZZVE10T2r"
                },
                "href": "https://api.spotify.com/v1/tracks/4PjcfyZZVE10TFd9Er",
                "id": "4PjcfyZZVE10TFd9EKA72r",
                "name": "Someday",
                "preview_url": "https://p.scdn.co/mp3-preview/2b15de922bf4f4f",
                "track_number": 2,
                "type": "track",
                "uri": "spotify:track:4PjcfyZZVE10TFd9EKA72r"
            }
        ],
        "limit": 50,
        "next": None,
        "offset": 0,
        "previous": None,
        "total": 11
    },
    "type": "album",
    "uri": "spotify:album:6akEvsycLGftJxYudPjmqK"
}

# Example EchoNest Genre Data
ECHONEST_ARTIST_GENRES = {
    'response': {
        'artist': {
            'genres': [
                {'name': 'dancehall'},
                {'name': 'reggae fusion'}
            ],
            'id': 'ARHMCWM1187FB37D67',
            'name': 'Damian Marley'
        },
        'status': {
            'code': 0,
            'message': 'Success',
            'version': '4.2'
        }
    }
}
