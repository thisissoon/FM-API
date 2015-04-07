#!/usr/bin/env python
# encoding: utf-8

"""
fm.user.routes
==============

Routes for the User Views
"""


from flask.ext.via.routers.default import Pluggable
from fm.views import user

routes = [
    # /users/current
    Pluggable('/authenticated', user.UserAuthenticatedView, 'authenticated'),
    # /users/{id}
    Pluggable('/<pk>', user.UserView, 'user'),

    Pluggable('/<pk>/spotify-playlists/',
              user.UserSpotifyPlaylistView, 'user_playlists')
]
