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
            'token': 'foo'
        }))

        assert response.status_code == 422
        request.assert_called_once_with(
            'https://accounts.google.com/o/oauth2/revoke?token=foo',
            'GET')
