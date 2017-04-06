#!/usr/bin/env python
# encoding: utf-8

"""
fm.config.default
=================

Default configuration for the Flask application.
"""

# Standard Libs
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
    'fm.tasks.artist',
    'fm.tasks.track',
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
SQLALCHEMY_DB_USER = os.environ.get(
    'SQLALCHEMY_DB_USER',
    'postgres')
SQLALCHEMY_DB_PASS = os.environ.get(
    'SQLALCHEMY_DB_PASS',
    'postgres')
SQLALCHEMY_DB_HOST = os.environ.get(
    'SQLALCHEMY_DB_HOST',
    'localhost')
SQLALCHEMY_DB_NAME = os.environ.get(
    'SQLALCHEMY_DB_NAME',
    'fm')
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
    'postgres://{0}:{1}@{2}:5432/{3}'.format(
        SQLALCHEMY_DB_USER,
        SQLALCHEMY_DB_PASS,
        SQLALCHEMY_DB_HOST,
        SQLALCHEMY_DB_NAME,
    )
)

# CORS

CORS_ACA_EXPOSE_HEADERS = ['Link', 'Total-Pages', 'Total-Count', 'Access-Token']
CORS_ACA_HEADERS = ['Content-Type', 'Access-Token']
CORS_ACA_ORIGIN = os.environ.get('CORS_ACA_ORIGIN', '*')

# Echo Nest

ECHONEST_API_KEY = os.environ.get('ECHONEST_API_KEY', None)

# Google OAuth

GOOGLE_ALLOWED_DOMAINS = [
    'thisissoon.com',
    'mentaltechnologies.com'
]
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', None)
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'postmessage')

# Spotify OAuth
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID', None)
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET', None)
SPOTIFY_REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI', 'postmessage')

# Known External Clients

EXTERNAL_CLIENTS = {
    'Soundwave': os.environ.get('SOUNDWAVE_PRIV_KEY', None),
    'Shockwave': os.environ.get('SHOCKWAVE_PRIV_KEY', None),
}
