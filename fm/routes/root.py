#!/usr/bin/env python
# encoding: utf-8

"""
fm.routes.root
==============

Base routes for the FM application using Flask-Via.
"""

# Third Party Libs
from flask.ext.via.routers import Include
from flask.ext.via.routers.default import Pluggable

# First Party Libs
from fm.views import RootView


routes = [
    # /
    Pluggable('/', RootView, 'root'),
    # /spotify/*
    Include('fm.routes.spotify', url_prefix='/spotify', endpoint='spotify'),
    # /player/*
    Include('fm.routes.player', url_prefix='/player', endpoint='player'),
    # /track/*
    Include('fm.routes.track', url_prefix='/tracks', endpoint='tracks'),
    # /oauth2/*
    Include('fm.routes.oauth2', url_prefix='/oauth2', endpoint='oauth2'),
    # /users/*
    Include('fm.routes.user', url_prefix='/users', endpoint='users'),
]
