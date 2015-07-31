#!/usr/bin/env python
# encoding: utf-8

"""
tests.test_clients
==================

Unittests for known client autnentication
"""

# Standard Libs
import base64
import hashlib
import hmac

# Third Party Libs
import mock

# First Party Libs
from fm.clients import get_private_key, valid_request, validate_signature


class TestGetPrivateKey(object):

    def test_should_return_none(self):
        assert get_private_key('foo') is None

    def test_should_return_key(self):
        self.app.config['EXTERNAL_CLIENTS']['FOO'] = 'bar'

        assert get_private_key('FOO') == 'bar'


class TestValidateSignature(object):

    @mock.patch('fm.clients.request')
    def test_return_false_no_match(self, _request):
        _request.data = 'foo'

        # Keys don't match
        key = 'bar'
        h = hmac.new('foo', 'foo', hashlib.sha256)
        sig = base64.b64encode(h.digest())

        assert validate_signature(key, sig) == False

    @mock.patch('fm.clients.request')
    def test_return_true(self, _request):
        _request.data = 'foo'

        key = 'foo'
        h = hmac.new('foo', 'foo', hashlib.sha256)
        sig = base64.b64encode(h.digest())

        assert validate_signature(key, sig)


class TestValidateRequest(object):

    @mock.patch('fm.clients.request')
    def test_invalid_or_no_client_id(self, _request):
        _request.headers = {}

        assert valid_request() == False

    @mock.patch('fm.clients.request')
    def test_invalid_auth_type(self, _request):
        _request.headers = {
            'Authorization': 'Foo Bar'
        }

        assert valid_request() == False

    @mock.patch('fm.clients.request')
    def test_invalid_auth_creds(self, _request):
        _request.headers = {
            'Authorization': 'HMAC Bar'
        }

        assert valid_request() == False

    @mock.patch('fm.clients.request')
    def test_invalid_request(self, _request):
        _request.headers = {
            'Authorization': 'HMAC foo:bar'
        }
        _request.data = 'foo'
        self.app.config['EXTERNAL_CLIENTS']['foo'] = 'bar'

        assert valid_request() == False

    @mock.patch('fm.clients.request')
    def test_valid_request(self, _request):
        h = hmac.new('foo', 'foo', hashlib.sha256)
        sig = base64.b64encode(h.digest())

        _request.headers = {
            'Authorization': 'HMAC foo:{0}'.format(sig)
        }
        _request.data = 'foo'
        self.app.config['EXTERNAL_CLIENTS']['foo'] = 'foo'

        assert valid_request()
