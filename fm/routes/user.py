#!/usr/bin/env python
# encoding: utf-8

"""
fm.user.routes
==============

Routes for the User Views
"""


# Third Pary Libs
from flask.ext.via.routers.default import Pluggable

# First Party Libs
from fm.views import user

routes = [
    # /users/current
    Pluggable('/authenticated', user.UserAuthenticatedView, 'authenticated'),
    # /users/{id}
    Pluggable('/<pk>', user.UserView, 'user'),

    Pluggable('/<user_pk>/spotify-playlists/',
              user.UserSpotifyPlaylistView, 'user_spotify_playlists'),
    Pluggable('/<user_pk>/spotify-playlists/<playlist_pk>',
              user.UserSpotifyTracksView, 'user_spotify_track')
]
