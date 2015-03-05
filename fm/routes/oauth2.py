#!/usr/bin/env python
# encoding: utf-8

"""
fm.routes.oauth2
================

Routes for the Google OAUTH2 Authentication
"""

from fm.views.oauth2 import TestFrontendView, OAuth2View
from flask.ext.via.routers.default import Pluggable


routes = [
    Pluggable('/test', TestFrontendView, 'test'),
    Pluggable('/test/connect', OAuth2View, 'connect'),
    Pluggable('/callback', OAuth2View, 'callback'),
]
