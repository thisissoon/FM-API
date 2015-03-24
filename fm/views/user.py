#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.user
=============

Views for working with User objects.
"""

import uuid


from flask.views import MethodView
from fm import http
from fm.models.user import User
from fm.session import authenticated, current_user
from fm.serializers.user import UserSeerialzer


class UserAuthenticatedView(MethodView):
    """ Authenticated User Resource - returns the currently authenticated user.
    """

    @authenticated
    def get(self):
        """ Returns the currently authenticated user
        """

        return http.OK(UserSeerialzer().serialize(current_user))


class UserView(MethodView):
    """ View for getting user object
    """

    def get(self, pk):
        """ Get a serialized user object.

        Arguments
        ---------
        pk : str
            The user primary key UUID
        """

        try:
            uuid.UUID(pk, version=4)
        except ValueError:
            user = None
        else:
            user = User.query.get(pk)

        if user is None:
            return http.NotFound()

        return http.OK(UserSeerialzer().serialize(user))
