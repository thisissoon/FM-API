#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.user.test_authenticated
====================================

Unit tests for the ``fm.views.user.UserAuthenticatedView`` class.
"""

from flask import g, url_for
from fm.ext import db
from fm.serializers.user import UserSerializer
from tests.factories.user import UserFactory


class TestUserAuthenticatedGet(object):

    def setup(self):
        # Create a user
        self.user = UserFactory()
        db.session.add(self.user)
        db.session.commit()
        g.user = self.user

    def must_be_authenticated(self):
        del g.user

        url = url_for('users.authenticated')
        response = self.client.get(url)

        assert response.status_code == 401

    def should_return_serialized_user(self):
        url = url_for('users.authenticated')
        response = self.client.get(url)

        expected = UserSerializer().serialize(self.user)

        assert response.status_code == 200
        assert response.json == expected
