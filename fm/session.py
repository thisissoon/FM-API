#!/usr/bin/env python
# encoding: utf-8

"""
fm.session
==========

Session handling functionality for user authentication using the `Access-Token`
header.
"""

# Standard Libs
from functools import wraps

# Third Party Libs
from flask import g, has_request_context, request
from itsdangerous import URLSafeTimedSerializer
from werkzeug import LocalProxy

# First Party Libs
from fm.ext import config, redis
from fm.http import Unauthorized
from fm.models.user import User


SESSION_KEY = 'fm:api:session:{0}'
USER_SESSION_KEY = 'fm:api:user:session:{0}'


current_user = LocalProxy(lambda: user_from_session())


def session_only_required(function):
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
    redis.sadd(USER_SESSION_KEY.format(pk), session_id)

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

    # Get the user id from the session in redis
    user_id = redis.get(SESSION_KEY.format(session_id))
    if user_id is None:
        return None

    user_key = USER_SESSION_KEY.format(user_id)

    # Convert fm:api:user:session:<user_id> to a set if a string
    if redis.type(user_key) == 'string':
        value = redis.get(user_key)
        redis.delete(user_key)
        redis.sadd(user_key, value)

    # Is the session id in the users sessions
    user_sessions = redis.smembers(user_key)
    if session_id not in user_sessions:
        return None

    serializer = URLSafeTimedSerializer(config.SECRET_KEY)
    if not serializer.loads(session_id) == user_id:
        return None

    return user_id


def user_from_session():
    """ Loads the user object from the request session.
    """

    auth_token_header = 'Access-Token'

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
