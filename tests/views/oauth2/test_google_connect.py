#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.oauth2.test_google_connect
======================================

Unit tests for the ``fm.views.oauth2.GoogleConnectView`` class.
"""

import json
import mock

from flask import url_for
from fm.models.user import User
from oauth2client.client import FlowExchangeError


class TestGoogleConnectPost(object):

    def setup(self):
        self.app.config['GOOGLE_CLIENT_ID'] = 'foo'
        self.app.config['GOOGLE_CLIENT_SECRET'] = 'bar'

    @mock.patch('fm.views.oauth2.httplib2.Http.request')
    @mock.patch('fm.views.oauth2.credentials_from_code')
    @mock.patch('fm.views.oauth2.google')
    def must_be_in_allowed_domains(self, google, credentials_from_code, request):
        credentials_from_code.return_value = mock.MagicMock(access_token='foo')

        service = mock.MagicMock()
        service.execute.return_value = {
            'domain': 'foo.com'
        }

        people = mock.MagicMock()
        people.get.return_value = service

        build = mock.MagicMock()
        build.people.return_value = people
        google.discovery.build.return_value = build

        url = url_for('oauth2.google.connect')
        response = self.client.post(url, data=json.dumps({
            'code': 'foo'
        }))

        assert response.status_code == 422
        request.assert_called_once_with(
            'https://accounts.google.com/o/oauth2/revoke?token=foo',
            'GET')

    @mock.patch('fm.views.oauth2.make_session')
    @mock.patch('fm.views.oauth2.httplib2.Http.request')
    @mock.patch('fm.views.oauth2.credentials_from_code')
    @mock.patch('fm.views.oauth2.google')
    def should_create_user(
            self,
            google,
            credentials_from_code,
            request,
            make_session):

        make_session.return_value = '123456.abcdefg'

        credentials_from_code.return_value = mock.MagicMock(
            access_token='foo',
            to_json=mock.Mock(return_value=json.dumps({'foo': 'bar'})))

        service = mock.MagicMock()
        service.execute.return_value = {
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
        }

        people = mock.MagicMock()
        people.get.return_value = service

        build = mock.MagicMock()
        build.people.return_value = people
        google.discovery.build.return_value = build

        assert User.query.count() == 0

        url = url_for('oauth2.google.connect')
        response = self.client.post(url, data=json.dumps({
            'code': 'foo'
        }))

        assert response.status_code == 201
        assert User.query.count() == 1
        assert response.headers['Auth-Token'] == '123456.abcdefg'
        assert 'Location' in response.headers

    @mock.patch('fm.views.oauth2.credentials_from_code')
    @mock.patch('fm.views.oauth2.google')
    def should_catch_flow_exceptions(self, google, credentials_from_code):
        credentials_from_code.return_value = mock.MagicMock(access_token='foo')
        credentials_from_code.side_effect = FlowExchangeError('some_error')

        url = url_for('oauth2.google.connect')
        response = self.client.post(url, data=json.dumps({
            'code': 'foo'
        }))

        assert response.status_code == 422
