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
    # /tracks
    Pluggable('', track.TracksView, 'collection'),
    # /tracks/{id}
    Pluggable('/<pk>', track.TrackVeiw, 'track')
]
