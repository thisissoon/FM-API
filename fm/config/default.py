#!/usr/bin/env python
# encoding: utf-8

"""
fm.config.default
=================

Default configuration for the Flask application.
"""

import os

# Player

PLAYER_CHANNEL = os.environ.get('PLAYER_CHANNEL', 'fm.player')

# Via

VIA_ROUTES_MODULE = 'fm.routes.root'

# Redis

REDIS_SERVER_URI = os.environ.get('REDIS_SERVER_URI')
REDIS_DB = os.environ.get('REDIS_DB')
