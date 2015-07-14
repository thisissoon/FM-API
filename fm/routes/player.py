#!/usr/bin/env python
# encoding: utf-8

"""
fm.routes.player
================

Route mapping to player resources.
"""

# Third Party Libs
from flask.ext.via.routers.default import Pluggable

# First Party Libs
from fm.views import player


routes = [
    Pluggable('/pause', player.PauseView, 'pause'),
    Pluggable('/current', player.CurrentView, 'current'),
    Pluggable('/history', player.HistoryView, 'history'),
    Pluggable('/stats', player.StatsView, 'stats'),
    Pluggable('/queue/', player.QueueView, 'queue'),
    Pluggable('/queue/<string:uuid>', player.QueueView, 'queue'),
    Pluggable('/queue/meta', player.QueueMetaView, 'queue-meta'),
    Pluggable('/volume', player.VolumeView, 'volume'),
    Pluggable('/mute', player.MuteView, 'mute'),
    Pluggable('/random', player.RandomView, 'random'),
]
