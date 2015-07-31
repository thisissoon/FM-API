#!/usr/bin/env python
# encoding: utf-8

"""
fm.clients
==========

Allow known external clients that are not users access to the API, these could
be the Player or Volume control systems for example which are physical boxes
that run outside of the network perimeter.

Clients should encode their request body with their private key using HMAC, this
should then be sent with the Authorization Header with the username being the
Clients ID and the password the signature.

Example
-------
    GET /foo
    Authorization: Soundwave frJIUN8DYpKDtOLCwo//yllqDzg=
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

    try:
        cid, sig = request.headers.get('Authorization', '').split()
    except ValueError:
        return False

    key = get_private_key(cid)
    if key is None:
        return False

    return False


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
