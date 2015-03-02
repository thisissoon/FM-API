#!/usr/bin/env python
# encoding: utf-8

"""
fm.app
======

Flask Application Factory for bootstraping the FM API Application.
"""

import os

from fm.ext import db, redis, via
from flask import Flask


def configure(app, config=None):
    """ Load application configuration from default module then overriding
    by environment variables, configs are loaded in the following order:

    1. Default config located in ``fm.config.default``
    2. ``FM_SETTINGS_MODULE`` OS Environment variable containing path to
       another config file.
    3. ``config`` keyword argument containing path to config file

    Arguments
    ---------
    app : flask.app.Flask
        Flask application instance
    config : str, optional
        Optional path to a settings file, defaults to ``None``
    """

    # Default configuration
    app.config.from_object('fm.config.default')

    # Override using os environment variable
    if os.environ.get('FM_SETTINGS_MODULE'):
        app.config.from_object(os.environ.get('FM_SETTINGS_MODULE'))

    # If override path is supplied use those settings
    if config:
        app.config.from_pyfile(config)


def create(config=None):
    """ Creates a Falsk Application instance.

    Arguments
    ---------
    config : str
        Path to a python configuration file
    """

    # Initialize Flask Application
    app = Flask(__name__)

    # Configure
    configure(app, config=config)

    # Reids
    redis.init_app(app)

    # SQLAlchemy
    db.init_app(app)

    # Routes
    via.init_app(app)

    return app
