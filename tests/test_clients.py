#!/usr/bin/env python
# encoding: utf-8

"""
tests.test_clients
==================

Unittests for known client autnentication
"""

# First Party Libs
from fm.clients import get_private_key


class TestGetPrivateKey(object):

    def test_should_return_none(self):
        assert get_private_key('foo') is None

    def test_should_return_key(self):
        self.app.config['EXTERNAL_CLIENTS']['FOO'] = 'bar'

        assert get_private_key('FOO') == 'bar'
