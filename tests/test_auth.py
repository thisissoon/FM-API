#!/usr/bin/env python
# encoding: utf-8

"""
tests.test_auth
===============

Unittests for the fm.auth module.
"""

# Third Party Libs
import mock

# First Party Libs
from fm.auth import authenticated, is_authenticated_request
from fm.http import Unauthorized


class TestAuthenticatedDecorator(object):

    @authenticated
    def i_am_protected(self):
        return True

    @mock.patch('fm.auth.is_authenticated_request')
    def test_returns_unauthorized(self, _is_authenticated_request):
        _is_authenticated_request.return_value = False

        response = self.i_am_protected()

        assert type(response) == Unauthorized

    @mock.patch('fm.auth.is_authenticated_request')
    def test_returns_resource(self, _is_authenticated_request):
        _is_authenticated_request.return_value = True

        assert self.i_am_protected()


class TestIsAuthenticatedRequest(object):

    def test_returns_false_by_default(self):
        assert is_authenticated_request() == False

    @mock.patch('fm.auth.session.user_from_session')
    def test_valid_session(self, _user_from_session):
        _user_from_session.return_value = True

        assert is_authenticated_request()

    @mock.patch('fm.auth.clients.valid_request')
    def test_valid_client(self, _valid_request):
        _valid_request.return_value = True

        assert is_authenticated_request()
