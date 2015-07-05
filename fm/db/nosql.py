#!/usr/bin/env python
# encoding: utf-8

"""
fm.db.nosql
===========

Classes for connecting to NoSQL data stores.
"""

# Standard Libs
import urlparse

# Third Party Libs
# Third Pary Libs
from redis import StrictRedis


class Redis(object):
    """ This class acts as a proxy to the main Redis class. To use this class
    instantiate it with a Flask application, this will then create the Redis
    connection and then use this instance to communicate with Redis.

    Example
    -------
        >>> from flask import Flask
        >>> from fm.db.nosql import Redis
        >>> app = Flask(__name__)
        >>> redis = Redis(app)
        >>> redis.set('x', 'y')
        >>> redis.get('x')
        ... 'y'
    """

    def __init__(self, app=None):
        """ Constructor, pass in an application object for usage outside an
        Application Factory.

        Arguments
        ---------
        app : flask.app.Flask
            Flask application instance
        """

        if app is not None:
            self.init_app(app)

    def __getattr__(self, name):
        """ Allows access to attributes on the Redis connection instance.

        Arguments
        ---------
        name : str
            Attribute name
        """

        if hasattr(self.connection, name):
            return getattr(self.connection, name)

        raise AttributeError

    def init_app(self, app):
        """ Initialise Redis for the Flask application from the application
        configuration.

        Arguments
        ---------
        app : flask.app.Flask
            Flask application instance
        """

        # Defaults
        app.config.setdefault('REDIS_SERVER_URI', 'redis://localhost:6379/')
        app.config.setdefault('REDIS_DB', 0)

        # Connect to Redis
        uri = urlparse.urlparse(app.config.get('REDIS_SERVER_URI'))
        self.connection = StrictRedis(
            host=uri.hostname,
            port=uri.port,
            password=uri.password,
            db=app.config.get('REDIS_DB'))
