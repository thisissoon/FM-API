#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.user
=============

Views for working with User objects.
"""


from flask.views import MethodView
from fm import http
from fm.models.user import User
from fm.serializers.user import UserSeerialzer


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

        user = User.query.get(pk)
        if user is None:
            return http.NotFound()

        return http.OK(UserSeerialzer().serialize(user))
