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
    GET / HTTP/1.1
    Accept: */*
    Accept-Encoding: gzip, deflate
    Authorization: HMAC client:fyKWDhnOjSnVyFZmfEEzwZM5/v4nWebca33eCYuLX9Q=
    Connection: keep-alive

Clients should use SHA256 to encode their requests and send a Base 64 encoded
version of the HMAC digest.
"""

# Standard Libs
import base64
import hashlib
import hmac
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
        auth_type, auth_creds = request.headers.get('Authorization', '').split()
    except ValueError:
        return False

    if not auth_type == 'HMAC':
        return False

    try:
        cid, sig = auth_creds.split(':')
    except ValueError:
        return False

    key = get_private_key(cid)
    if key is None:
        return False

    return validate_signature(key, sig)


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


def validate_signature(key, expected):
    """ Validates the HMAC signature sent with the request, encoding the raw
    request body and comparing the signatures.

    Arguments
    ---------
    key : str
        The client private key
    expected : str
        The signature expected

    Returns
    -------
    bool
        If the signatures match
    """

    # Generates a hex of the request digest based on the secret key
    sig = base64.b64encode(hmac.new(key, request.data, hashlib.sha256).digest())

    # Return if they match or not
    return sig == expected
