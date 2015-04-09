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

# Server Name

SERVER_NAME = os.environ.get('SERVER_NAME')

# Secret

SECRET_KEY = 'CHANGEME'  # Changed for other environments

# Celery

CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_URL = os.environ.get(
    'CELERY_BROKER_URL',
    'amqp://guest:guest@localhost:5672//')
CELERY_IMPORTS = (
    'fm.tasks.queue'
)
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

# Player

PLAYER_CHANNEL = os.environ.get('PLAYER_CHANNEL', 'fm:events')
PLAYLIST_REDIS_KEY = os.environ.get('PLAYLIST_KEY', 'fm:player:queue')

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

# CORS

CORS_ACA_EXPOSE_HEADERS = ['Link', 'Total-Pages', 'Total-Count', 'Access-Token']
CORS_ACA_HEADERS = ['Content-Type', 'Access-Token']
CORS_ACA_ORIGIN = os.environ.get('CORS_ACA_ORIGIN', '*')

# Google OAuth
GOOGLE_ALLOWED_DOMAINS = [
    'thisissoon.com',
    'thishe.re'
]
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', None)
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'postmessage')
