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
    Pluggable('/pause', player.PauseView, 'pause'),
    Pluggable('/current', player.CurrentView, 'current'),
    Pluggable('/queue', player.QueueView, 'queue'),
]
