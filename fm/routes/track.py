#!/usr/bin/env python
# encoding: utf-8

"""
fm.routes.track
===============

Routes for handling Tracks.
"""


from flask.ext.via.routers.default import Pluggable
from fm.views import track


routes = [
    # /track
    Pluggable('/track', track.Tracks, 'collection'),
    # /track/{id}
    Pluggable('/track/<id>', track.Track, 'object')
]
