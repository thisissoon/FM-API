#!/usr/bin/env python
# encoding: utf-8

"""
fm.session
==========

Session handling functionality for user authentication using the `Auth-Token`
header.
"""

from flask import g, request, has_request_context
from fm.ext import config, redis
from fm.models.user import User
from functools import wraps
from itsdangerous import URLSafeTimedSerializer
from werkzeug import LocalProxy

from fm.http import Unauthorized


SESSION_KEY = 'fm:api:session:{0}'
USER_SESSION_KEY = 'fm:api:user:session:{0}'


current_user = LocalProxy(lambda: user_from_session())


def authenticated(function):
    """ Decorator which requires that the view is accessable only to users
    with a valid session.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        user = user_from_session()
        if user is None:
            return Unauthorized()
        return function(*args, **kwargs)

    return wrapper


def make_session(pk):
    """ Creates a new Session ID for the user expiaring the old session if
    one exists. This will be called on Google OAuth Connection (Login).

    Arguments
    ---------
    pk : str
        The user primary key UUID

    Returns
    -------
    str
        The new Session ID
    """

    serializer = URLSafeTimedSerializer(config.SECRET_KEY)
    session_id = serializer.dumps(pk)

    redis.set(SESSION_KEY.format(session_id), pk)
    redis.set(USER_SESSION_KEY.format(pk), session_id)

    return session_id


def validate_session(session_id):
    """ Validates an incoming Session ID, ensures that it is valid
    by ensuring it matches with the correct user.

    Arguments
    ---------
    session_id : str
        The Session ID to Validate

    Returns
    -------
    str or None
        User primary key or None if session is not valid
    """

    user_id = redis.get(SESSION_KEY.format(session_id))
    if user_id is None:
        return None

    user_session_id = redis.get(USER_SESSION_KEY.format(user_id))
    if user_session_id is None:
        return None
    if not user_session_id == session_id:
        return None

    serializer = URLSafeTimedSerializer(config.SECRET_KEY)
    if not serializer.loads(session_id) == user_id:
        return None

    return user_id


def user_from_session():
    """ Loads the user object from the request session.
    """

    auth_token_header = 'Auth-Token'

    # If the request has context and the user is not part of the request
    # stack we load the user
    if has_request_context() and not hasattr(g, 'user'):
        if auth_token_header in request.headers:
            session_id = request.headers.get(auth_token_header)
            user_id = validate_session(session_id)
            if user_id is not None:
                user = User.query.get(user_id)
                if user is not None:
                    g.user = user

    return getattr(g, 'user', None)
