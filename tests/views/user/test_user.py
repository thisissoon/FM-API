#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.user.test_user
==========================

Unit tests for the ``fm.views.user.UserView`` class.
"""

# Standard Libs
import uuid

# Third Pary Libs
from flask import url_for

# First Party Libs
from fm.ext import db
from fm.serializers.user import UserSerializer
from tests.factories.user import UserFactory


class TestUserGet(object):

    def must_be_valid_uuid(self):
        url = url_for('users.user', pk='foo')
        response = self.client.get(url)

        assert response.status_code == 404

    def should_return_not_found(self):
        url = url_for('users.user', pk=unicode(uuid.uuid4()))
        response = self.client.get(url)

        assert response.status_code == 404

    def should_return_serialized_user(self):
        user = UserFactory()

        db.session.add(user)
        db.session.commit()

        url = url_for('users.user', pk=user.id)
        response = self.client.get(url)

        expected = UserSerializer().serialize(user)

        assert response.status_code == 200
        assert response.json == expected
