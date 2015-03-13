#!/usr/bin/env python
# encoding: utf-8

"""
fm.routes.root
==============

Base routes for the FM application using Flask-Via.
"""


from fm.views import RootView
from flask.ext.via.routers import Include
from flask.ext.via.routers.default import Pluggable


routes = [
    # /
    Pluggable('/', RootView, 'root'),
    # /player/*
    Include('fm.routes.player', url_prefix='/player', endpoint='player'),
    # /track/*
    Include('fm.routes.track', url_prefix='/tracks', endpoint='tracks')
]
