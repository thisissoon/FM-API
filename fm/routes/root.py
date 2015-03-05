#!/usr/bin/env python
# encoding: utf-8

"""
fm.routes.root
==============

Base routes for the FM application using Flask-Via.
"""


from flask.ext.via.routers import Include


routes = [
    # /player/*
    Include('fm.routes.player', url_prefix='/player', endpoint='player'),
    # /track/*
    Include('fm.routes.track', url_prefix='/tracks', endpoint='tracks'),
    # /oauth2/*
    Include('fm.routes.oauth2', url_prefix='/oauth2', endpoint='oauth2')
]
