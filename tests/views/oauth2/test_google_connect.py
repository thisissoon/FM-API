#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.oauth2.test_google_connect
======================================

Unit tests for the ``fm.views.oauth2.GoogleConnectView`` class.
"""

# Standard Libs
import json

# Third Pary Libs
import mock
from flask import url_for

# First Party Libs
from fm.models.user import User
from fm.oauth2.google import GoogleOAuth2Exception


class TestGoogleConnectPost(object):

    def setup(self):
        self.app.config['GOOGLE_CLIENT_ID'] = 'foo'
        self.app.config['GOOGLE_CLIENT_SECRET'] = 'bar'

    @mock.patch('fm.views.oauth2.make_session')
    @mock.patch('fm.views.oauth2.authenticate_oauth_code')
    def should_create_user(self, authenticate_oauth_code, make_session):
        authenticate_oauth_code.return_value = (
            {
                'id': u'123456',
                'domain': 'thisissoon.com',
                'emails': [{'value': 'foo@thisissoon.com'}],
                'name': {
                    'givenName': 'Foo',
                    'familyName': 'Bar',
                },
                'displayName': 'FooBar',
                'image': {
                    'url': 'http://foo.com/foo.jpg?sz=60x60'
                }
            },
            mock.MagicMock(
                access_token='foo',
                to_json=mock.Mock(return_value=json.dumps({'foo': 'bar'})))
        )
        make_session.return_value = '123456.abcdefg'

        assert User.query.count() == 0

        url = url_for('oauth2.google.connect')
        response = self.client.post(url, data=json.dumps({
            'code': 'foo'
        }))

        assert response.status_code == 201
        assert User.query.count() == 1
        assert response.json['access_token'] == '123456.abcdefg'
        assert 'Location' in response.headers

    @mock.patch('fm.views.oauth2.authenticate_oauth_code')
    def should_catch_exceptions(self, authenticate_oauth_code):
        authenticate_oauth_code.side_effect = GoogleOAuth2Exception('some_error')

        url = url_for('oauth2.google.connect')
        response = self.client.post(url, data=json.dumps({
            'code': 'foo'
        }))

        assert response.status_code == 422
        assert 'some_error' in response.json['errors']['code']
