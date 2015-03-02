#!/usr/bin/env python
# encoding: utf-8

"""
fm.config.default
=================

Default configuration for the Flask application.
"""

import os

# Debugging

DEBUG = True

# Celery

CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_URL = os.environ.get(
    'CELERY_BROKER_URL',
    'amqp://guest:guest@localhost:5672//')
CELERY_IMPORTS = (
    'fm.tasks.add',
)
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

# Player

PLAYER_CHANNEL = os.environ.get('PLAYER_CHANNEL', 'fm.player')

# Via

VIA_ROUTES_MODULE = 'fm.routes.root'

# Redis

REDIS_SERVER_URI = os.environ.get(
    'REDIS_SERVER_URI',
    'redis://localhost:6379/')
REDIS_DB = os.environ.get('REDIS_DB', 0)

# SQLAlchemy

SQLALCHEMY_NATIVE_UNICODE = False
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
    'sqlite://:memory:')
