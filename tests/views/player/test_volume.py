#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_volume
==============================

Unit tests for the ``fm.views.player.VolumeView`` class.
"""

# Standard Libs
import json

# Third Party Libs
import mock
import pytest
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
        assert response.json['volume'] == 0

    def should_return_current_volume(self):
        self.redis.get.return_value = 70

        url = url_for('player.volume')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['volume'] == 70


@pytest.mark.usefixtures("authenticated")
class TestVolumePost(BaseVolumeTest):

    @pytest.mark.usefixtures("unauthenticated")
    def must_be_authenticated(self):
        url = url_for('player.mute')
        response = self.client.delete(url)

        assert response.status_code == 401

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
        assert response.json == {'volume': 20}
