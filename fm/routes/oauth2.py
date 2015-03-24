#!/usr/bin/env python
# encoding: utf-8

"""
fm.routes.oauth2
================

Routes for the Google OAUTH2 Authentication
"""

from fm.views import oauth2
from flask.ext.via.routers.default import Pluggable


routes = [
    Pluggable('/google/client', oauth2.GoogleTestClientView, 'google.test'),
    Pluggable('/google/connect', oauth2.GoogleConnectView, 'google.connect')
]
