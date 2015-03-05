#!/usr/bin/env python
# encoding: utf-8

"""
fm.routes.oauth2
================

Routes for the Google OAUTH2 Authentication
"""

from fm.views.oauth2 import TestFrontendView
from flask.ext.via.routers.default import Pluggable


routes = [
    Pluggable('/test', TestFrontendView, 'test')
]
