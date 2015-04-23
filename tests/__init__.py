#!/usr/bin/env python
# encoding: utf-8

"""
tests
=====

Test suite for FM Player setup.
"""

import os


# Set Tests to user Test Config
os.environ['FM_SETTINGS_MODULE'] = 'fm.config.test'

# Example response from Spotify Track API
TRACK_DATA = {
    u'album': {
        u'album_type': u'album',
        u'available_markets': [u'GB'],
        u'external_urls': {
            u'spotify': u'https://open.spotify.com/album/5SpcwnEVClk33l5QM04vSy'
        },
        u'href': u'https://api.spotify.com/v1/albums/5SpcwnEVClk33l5QM04vSy',
        u'id': u'5SpcwnEVClk33l5QM04vSy',
        u'images': [
            {
                u'height': 640,
                u'url': u'https://i.scdn.co/image/770cfef8e832ae47139debe788f7c11afb92a816',
                u'width': 640
            }, {
                u'height': 300,
                u'url': u'https://i.scdn.co/image/dcb8f435712888a71f4106b1ed83da9e6713e1e0',
                u'width': 300
            }, {
                u'height': 64,
                u'url': u'https://i.scdn.co/image/8a87ca6a9fc52e63c1c69f32d14c9bbec2ac0e77',
                u'width': 64
            }
        ],
        u'name': u'Devotion',
        u'type': u'album',
        u'uri': u'spotify:album:5SpcwnEVClk33l5QM04vSy'
    },
    u'artists': [
        {
            u'external_urls': {
                u'spotify': u'https://open.spotify.com/artist/5v61OSg53KaQxGMpErkBNp'
            },
            u'href': u'https://api.spotify.com/v1/artists/5v61OSg53KaQxGMpErkBNp',
            u'id': u'5v61OSg53KaQxGMpErkBNp',
            u'name': u'Anberlin',
            u'type': u'artist',
            u'uri': u'spotify:artist:5v61OSg53KaQxGMpErkBNp'
        }
    ],
    u'available_markets': [u'GB'],
    u'disc_number': 1,
    u'duration_ms': 201806,
    u'explicit': False,
    u'external_ids': {
        u'isrc': u'USUM71210069'
    },
    u'external_urls': {
        u'spotify': u'https://open.spotify.com/track/11oRv2sfZJxNYqCl6wLaqJ'
    },
    u'href': u'https://api.spotify.com/v1/tracks/11oRv2sfZJxNYqCl6wLaqJ',
    u'id': u'11oRv2sfZJxNYqCl6wLaqJ',
    u'name': u'Little Tyrants',
    u'popularity': 32,
    u'preview_url': u'https://p.scdn.co/mp3-preview/93d539cdfc573ae899bfc57245acfbdae29a70e5',
    u'track_number': 2,
    u'type': u'track',
    u'uri': u'spotify:track:11oRv2sfZJxNYqCl6wLaqJ'
}


# Example EchoNest Genre Data
ECHONEST_ARTIST_GENRES = {
    u'response': {
        u'artist': {
            u'genres': [
                {u'name': u'dancehall'},
                {u'name': u'reggae fusion'}
            ],
            u'id': u'ARHMCWM1187FB37D67',
            u'name': u'Damian Marley'
        },
        u'status': {
            u'code': 0,
            u'message': u'Success',
            u'version': u'4.2'
        }
    }
}
