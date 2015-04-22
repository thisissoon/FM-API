#!/usr/bin/env python
# encoding: utf-8

"""
fm.routes.player
================

Route mapping to player resources.
"""


# Third Pary Libs
from flask.ext.via.routers.default import Pluggable

# First Party Libs
from fm.views import player


routes = [
    Pluggable('/pause', player.PauseView, 'pause'),
    Pluggable('/current', player.CurrentView, 'current'),
    Pluggable('/history', player.HistoryView, 'history'),
    Pluggable('/queue', player.QueueView, 'queue'),
    Pluggable('/volume', player.VolumeView, 'volume'),
    Pluggable('/mute', player.MuteView, 'mute'),
    Pluggable('/random', player.RandomView, 'random'),
]
