#!/usr/bin/env python
# encoding: utf-8

"""
tests.test_session
==================

Unit tests for session management.
"""

import mock
import uuid

from fm.ext import db
from fm.session import user_from_session
from tests.factories.user import UserFactory


class TestUserFromSession(object):

    @mock.patch('fm.session.request')
    def ensure_no_auth_token_returns_none(self, request):
        request.headers = {}

        assert user_from_session() is None

    @mock.patch('fm.session.validate_session')
    @mock.patch('fm.session.request')
    def ensure_invalid_auth_token_returns_none(
            self,
            request,
            validate_session):
        request.headers = {'Auth-Token': 'foo'}
        validate_session.return_value = None

        assert user_from_session() is None

    @mock.patch('fm.session.validate_session')
    @mock.patch('fm.session.request')
    def ensure_user_exists(self, request, validate_session):
        request.headers = {'Auth-Token': 'foo'}
        validate_session.return_value = unicode(uuid.uuid4())

        assert user_from_session() is None

    @mock.patch('fm.session.validate_session')
    @mock.patch('fm.session.request')
    def should_return_user_instance(self, request, validate_session):
        user = UserFactory()

        db.session.add(user)
        db.session.commit()

        request.headers = {'Auth-Token': 'foo'}
        validate_session.return_value = user.id

        assert user_from_session() == user
