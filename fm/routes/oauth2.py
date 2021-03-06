#!/usr/bin/env python
# encoding: utf-8

"""
fm.routes.oauth2
================

Routes for the Google OAUTH2 Authentication
"""
# Third Party Libs
from flask.ext.via.routers.default import Pluggable

# First Party Libs
from fm.views import oauth2


routes = [
    Pluggable('/google/client', oauth2.GoogleTestClientView, 'google.test'),
    Pluggable('/google/connect', oauth2.GoogleConnectView, 'google.connect'),

    Pluggable('/spotify/client', oauth2.SpotifyTestClientView, 'spotify.test'),
    Pluggable('/spotify/connect', oauth2.SpotifyConnectView, 'spotify.connect'),
]
