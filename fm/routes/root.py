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
    Include('fm.routes.player', url_prefix='/player', endpoint='player')
]
