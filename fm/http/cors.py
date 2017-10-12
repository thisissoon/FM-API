#!/usr/bin/env python
# encoding: utf-8

"""
fm.http.cors
============

Cross Origin Request Handling.
"""
# Third Party Libs
from flask import request


HEADERS = {
    'METHODS': 'Access-Control-Allow-Methods',
    'CREDENTIALS': 'Access-Control-Allow-Credentials',
    'ORIGIN': 'Access-Control-Allow-Origin',
    'MAX_AGE': 'Access-Control-Allow-Max-Age',
    'EXPOSE_HEADERS': 'Access-Control-Expose-Headers',
    'HEADERS': 'Access-Control-Allow-Headers'
}


class CORS(object):

    def __init__(self, app=None):
        """ Constructor
        """

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """ Initialises CORS for the Flask application
        """

        self.set_config_defaults(app)

        def after_request(response):
            """ After request response handling, to append CORS headers to
            the response.
            """

            response.headers[HEADERS['CREDENTIALS']] = app.config['CORS_ACA_CREDENTIALS']

            for origin in app.config['CORS_ACA_ORIGIN'].split(","):
                if origin == request.headers.get('ORIGIN'):
                    response.headers[HEADERS['ORIGIN']] = origin
                    break

            if expose_headers(app) is not None:
                response.headers[HEADERS['EXPOSE_HEADERS']] = expose_headers(app)

            if request.method == 'OPTIONS':
                response.headers[HEADERS['METHODS']] = methods()
                response.headers[HEADERS['MAX_AGE']] = app.config['CORS_ACA_MAX_AGE']

                if headers(app) is not None:
                    response.headers[HEADERS['HEADERS']] = headers(app)

            return response

        app.after_request(after_request)

    def set_config_defaults(self, app):
        """ Sets sane configuration defaults for CORS.
        """

        app.config.setdefault('CORS_ACA_CREDENTIALS', 'true')
        app.config.setdefault('CORS_ACA_ORIGIN', '*')
        app.config.setdefault('CORS_ACA_MAX_AGE', 86400)
        app.config.setdefault('CORS_ACA_EXPOSE_HEADERS', [])
        app.config.setdefault('CORS_ACA_HEADERS', [])


def methods():
    """ For the request url only allow methods that the view supports.
    """

    methods = list(request.url_rule.methods)

    return ', '.join(methods)


def expose_headers(app):
    """ Returns string version of exposed headers for the
    ``Access-Control-Allow-Expose-Headers`` header value.
    """

    if len(app.config['CORS_ACA_EXPOSE_HEADERS']) > 0:
        return ', '.join(app.config['CORS_ACA_EXPOSE_HEADERS'])

    return None


def headers(app):
    """ Returns string version of headers for the
    ``Access-Control-Allow-Headers`` header value.
    """

    if len(app.config['CORS_ACA_HEADERS']) > 0:
        return ', '.join(app.config['CORS_ACA_HEADERS'])

    return None
