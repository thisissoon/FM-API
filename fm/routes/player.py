#!/usr/bin/env python
# encoding: utf-8

"""
fm.routes.player
================

Route mapping to player resources.
"""


from flask.ext.via.routers.default import Pluggable
from fm.views import player


routes = [
    # /player/pause
    Pluggable('/pause', player.Pause, 'pause'),
    # /player/playlist
    Pluggable('/playlist', player.Playlist, 'playlist'),
]
