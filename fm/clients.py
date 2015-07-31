#!/usr/bin/env python
# encoding: utf-8

"""
fm.clients
==========

Allow known external clients that are not users access to the API, these could
be the Player or Volume control systems for example which are physical boxes
that run outside of the network perimeter.

Clients should send a Client-ID header which will correlate to a Private Key
stored both on the Client and the Server. The Client will encode their request
with this key, the server will check the request validity by also encoding
the raw request with the same key and ensuring they match, this is known as
HMAC.
"""

# Standard Libs
from functools import wraps

# Third Party Libs
from flask import current_app, request

# First Party Libs
from fm.http import Unauthorized


def known_client(function):
    """ Decorator which requires that the view is accessible by only
    known external clients.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        if not valid_request():
            return Unauthorized()
        return function(*args, **kwargs)

    return wrapper


def valid_request():
    """ Validates an incoming request from and ensures it comes from a trusted
    source.

    Returns
    -------
    bool
        If the request is from a trust client
    """

    pass


def get_private_key(client_id):
    """ Gets the private key for the client from Flask application
    configuration.

    Example
    -------
        >>> EXTERNAL_CLIENTS = {
        >>>     'Client-ID': 'PrivateKey'
        >>> }

    Returns
    -------
    str or None
        The clients private key or None if the client is not found
    """

    clients = current_app.config.get('EXTERNAL_CLIENTS', {})
    key = clients.get(client_id, None)

    return key
