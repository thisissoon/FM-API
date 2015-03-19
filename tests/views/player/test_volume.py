#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_volume
==============================

Unit tests for the ``fm.views.player.VolumeView`` class.
"""

import json
import mock

from flask import url_for


class BaseVolumeTest(object):

    def setup(self):
        patch = mock.patch('fm.views.player.redis')
        self.redis = patch.start()
        self.addPatchCleanup(patch)


class TestVolumeGet(BaseVolumeTest):

    def should_return_100_if_invalid_value(self):
        self.redis.get.return_value = 'foo'

        url = url_for('player.volume')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['volume'] == 100

    def should_return_current_volume(self):
        self.redis.get.return_value = 70

        url = url_for('player.volume')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['volume'] == 70


class TestVolumePost(BaseVolumeTest):

    def must_not_be_over_100(self):
        url = url_for('player.volume')
        response = self.client.post(url, data=json.dumps({
            'volume': 150
        }))

        assert response.status_code == 422
        assert 'volume' in response.json['errors']

    def must_not_be_less_than_0(self):
        url = url_for('player.volume')
        response = self.client.post(url, data=json.dumps({
            'volume': -10
        }))

        assert response.status_code == 422
        assert 'volume' in response.json['errors']

    def should_publish_set_volume_event(self):
        url = url_for('player.volume')
        response = self.client.post(url, data=json.dumps({
            'volume': 20
        }))

        assert response.status_code == 200
        self.redis.publish.assert_called_once_with(
            self.app.config.get('PLAYER_CHANNEL'),
            json.dumps({
                'event': 'set_volume',
                'volume': 20
            }))
