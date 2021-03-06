#!/usr/bin/env python
# encoding: utf-8

"""
fm.app
======

Flask Application Factory for bootstraping the FM API Application.
"""

# Standard Libs
import os
import traceback

# Third Party Libs
from flask import Flask, request

# First Party Libs
from fm import models  # noqa
from fm import http
from fm.ext import celery, db, redis, via
from fm.http.cors import CORS
import fm.logs


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


def errors(app):
    """ Sets up error handlers for catching thrown errors by Flask.
    """

    @app.errorhandler(400)
    def handle_400(e):
        """ Handle 400's - This can be thrown when the request body cannot
        be decoded, for example malformed JSON.
        """

        response = {
            'message': 'Bad Request'
        }

        return http.BadRequest(response)

    @app.errorhandler(404)
    def handle_404(e):
        """ Handle 404 errors.
        """

        response = {
            'message': 'Not Found'
        }

        return http.NotFound(response)

    @app.errorhandler(Exception)
    def handle_uncaught_error(e):
        """ Handle uncaught errors from the BE. Always returns a 500. If
        the application is in debug mode the traceback will also be
        returned in the response object.
        """

        response = {
            'message': 'Unknown Error'
        }

        if app.debug:
            response['traceback'] = traceback.format_exc()

        return http.InternalServerError(response)


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

    # Celery
    celery.init_app(app)

    # Reids
    redis.init_app(app)

    # SQLAlchemy
    db.init_app(app)

    # Routes
    via.init_app(app)

    # Cross Origin
    CORS(app)

    # Error Handling
    errors(app)

    fm.logs.configure(app)

    @app.before_request
    def require_json():
        """ Ensures the API only supports JSON in.
        """

        if request.method in ['PUT', 'POST']:
            if not request.mimetype == 'application/json':
                return http.UnsupportedMediaType()

    return app
