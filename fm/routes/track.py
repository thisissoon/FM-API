#!/usr/bin/env python
# encoding: utf-8

"""
fm.routes.track
===============

Routes for handling Tracks.
"""


# Third Pary Libs
from flask.ext.via.routers.default import Pluggable

# First Party Libs
from fm.views import track


routes = [
    # /tracks
    Pluggable('', track.TracksView, 'collection'),
    # /tracks/{id}
    Pluggable('/<pk_or_uri>', track.TrackVeiw, 'track')
]
