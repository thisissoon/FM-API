#!/usr/bin/env python
# encoding: utf-8

"""
tests.test_session
==================

Unit tests for session management.
"""

import mock
import uuid

from flask import g
from fm.ext import db
from fm.http import Unauthorized
from fm.session import (
    SESSION_KEY,
    USER_SESSION_KEY,
    authenticated,
    make_session,
    validate_session,
    user_from_session)
from itsdangerous import URLSafeTimedSerializer
from tests.factories.user import UserFactory


class TestAuthenticated(object):

    @authenticated
    def i_am_protected(self):
        return True

    @mock.patch('fm.session.user_from_session')
    def should_return_unauthorized_on_failure(self, user_from_session):
        user_from_session.return_value = None

        response = self.i_am_protected()

        assert type(response) == Unauthorized

    @mock.patch('fm.session.user_from_session')
    def should_allow_access(self, user_from_session):
        user_from_session.return_value = mock.MagicMock()

        response = self.i_am_protected()

        assert response is True


class TestMakeSession(object):

    @mock.patch('fm.session.URLSafeTimedSerializer')
    @mock.patch('fm.session.redis')
    def tests_makes_session(self, redis, URLSafeTimedSerializer):
        serializer = mock.MagicMock()
        serializer.dumps.return_value = 'foobar'
        URLSafeTimedSerializer.return_value = serializer

        assert make_session('1234') == 'foobar'
        redis.set.assert_has_call(SESSION_KEY.format('foobar'), '1234')
        redis.set.assert_has_call(USER_SESSION_KEY.format('1234'), 'foobar')


class TestValidateSession(object):

    def setup(self):
        patch = mock.patch('fm.session.redis')
        self.redis = patch.start()
        self.addPatchCleanup(patch)

    def ensure_no_session_key_retuens_none(self):
        self.redis.get.return_value = None

        assert validate_session('foo') is None

    def ensure_session_id_in_user_sessions(self):
        self.redis.get.return_value = '1234',
        self.redis.smembers.return_value = set(['4567'])

        assert validate_session('foo') is None

    def ensure_user_ids_match(self):
        serializer = URLSafeTimedSerializer(self.app.config['SECRET_KEY'])
        session_id = serializer.dumps('1234')

        self.redis.get.return_value = '4567'
        self.redis.smembers.return_value = set([session_id])

        assert validate_session(session_id) is None

    def should_return_user_id(self):
        serializer = URLSafeTimedSerializer(self.app.config['SECRET_KEY'])
        session_id = serializer.dumps('1234')

        self.redis.get.return_value = '1234'
        self.redis.smembers.return_value = set([session_id])

        assert validate_session(session_id) is '1234'


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
        request.headers = {'Access-Token': 'foo'}
        validate_session.return_value = None

        assert user_from_session() is None

    @mock.patch('fm.session.validate_session')
    @mock.patch('fm.session.request')
    def ensure_user_exists(self, request, validate_session):
        request.headers = {'Access-Token': 'foo'}
        validate_session.return_value = unicode(uuid.uuid4())

        assert user_from_session() is None

    @mock.patch('fm.session.validate_session')
    @mock.patch('fm.session.request')
    def should_return_user_instance(self, request, validate_session):
        user = UserFactory()

        db.session.add(user)
        db.session.commit()

        request.headers = {'Access-Token': 'foo'}
        validate_session.return_value = user.id

        assert user_from_session() == user

    def should_return_user_already_on_stack(self):
        g.user = UserFactory()

        assert user_from_session() == g.user
