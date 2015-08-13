#!/usr/bin/env python
# encoding: utf-8

"""
fm.auth
=======

Authentication decorators
"""

# Standard Libs
from functools import wraps

# First Party Libs
from fm import clients, session
from fm.http import Unauthorized


def authenticated(function):
    """ This decorator handles allowing access to tesources based on session
    or known clients.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        if not is_authenticated_request():
            return Unauthorized()
        return function(*args, **kwargs)

    return wrapper


def is_authenticated_request():
    """ Retruns if the request is valid

    Returns
    -------
    bool
        If the requets is valid
    """

    # Known client?
    if clients.valid_request():
        return True

    # Is a user session?
    user = session.user_from_session()
    if user is not None:
        return True

    return False
