#!/usr/bin/env python
# encoding: utf-8

"""
tests.test_google
=================

Tests for Google OAuth2 helpers.
"""

import mock
import pytest

from fm import google
from oauth2client.client import FlowExchangeError


class TestGetCredentials(object):

    def setup(self):
        self.app.config['GOOGLE_CLIENT_ID'] = 'foo'
        self.app.config['GOOGLE_CLIENT_SECRET'] = 'bar'
        self.app.config['GOOGLE_REDIRECT_URI'] = 'bar'

    @mock.patch('fm.google.credentials_from_code')
    def must_crach_flow_exception_and_reraise(self, credentials_from_code):
        credentials_from_code.return_value = mock.MagicMock(access_token='bar')
        credentials_from_code.side_effect = FlowExchangeError('some_error')

        with pytest.raises(google.GoogleOAuth2Exception):
            google.get_credentials('foo')


class TestDisconnect(object):

    @mock.patch('fm.google.httplib2')
    def should_raise_exception_on_invalid_status(self, httplib2):
        Http = mock.MagicMock()
        Http.request.return_value = ({'status': '400'}, )

        httplib2.Http.return_value = Http

        with pytest.raises(google.GoogleOAuth2Exception):
            google.disconnect('foo')

    @mock.patch('fm.google.httplib2')
    def should_disconnect_user(self, httplib2):
        Http = mock.MagicMock()
        Http.request.return_value = ({'status': '200'}, )

        httplib2.Http.return_value = Http

        google.disconnect('foo')

        Http.request.assert_called_once_with(
            'https://accounts.google.com/o/oauth2/revoke?token=foo',
            'GET')


class TestAuthenticateOauthCode(object):

    @mock.patch('fm.google.get_credentials')
    @mock.patch('fm.google.user_from_credentials')
    @mock.patch('fm.google.disconnect')
    def must_raise_exception_not_in_allowed_domains(
            self,
            disconnect,
            user_from_credentials,
            get_credentials):

        get_credentials.return_value = mock.MagicMock(access_token='bar')
        user_from_credentials.return_value = {'domain': 'foo.com'}

        with pytest.raises(google.GoogleOAuth2Exception):
            google.authenticate_oauth_code('foo')
            disconnect.assert_called_once_with('bar')
