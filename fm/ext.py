#!/usr/bin/env python
# encoding: utf-8

"""
fm.ext
======

Flask Application Extension Instantiation.
"""

from flask.ext.via import Via
from fm.db.nosql import Redis

# Flask-Via for Routing Modules
via = Via()

# Redis -  Stores application state
redis = Redis()
