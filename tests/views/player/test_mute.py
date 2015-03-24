#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_must
============================

Unit tests for the ``fm.views.player.MuteView`` class.
"""

import json
import mock
import pytest

from flask import url_for


class BaseMuteTest(object):

    def setup(self):
        patch = mock.patch('fm.views.player.redis')
        self.redis = patch.start()
        self.addPatchCleanup(patch)


class TestGetMute(BaseMuteTest):

    def should_return_current_mute_state(self):
        self.redis.get.return_value = 1

        url = url_for('player.mute')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['mute'] == True

    def must_return_false_if_not_set(self):
        self.redis.get.return_value = None

        url = url_for('player.mute')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['mute'] == False

    def ensure_invalid_state_is_false(self):
        self.redis.get.return_value = 'foo'

        url = url_for('player.mute')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['mute'] == False


@pytest.mark.usefixtures("authenticated")
class TestPostMute(BaseMuteTest):

    @pytest.mark.usefixtures("unauthenticated")
    def must_be_authenticated(self):
        url = url_for('player.mute')
        response = self.client.post(url)

        assert response.status_code == 401

    def should_fire_redis_mute_event(self):
        url = url_for('player.mute')
        response = self.client.post(url)

        assert response.status_code == 201
        self.redis.publish.assert_called_once_with(
            self.app.config.get('PLAYER_CHANNEL'),
            json.dumps({
                'event': 'set_mute',
                'mute': True
            }))


@pytest.mark.usefixtures("authenticated")
class TestDeleteMute(BaseMuteTest):

    @pytest.mark.usefixtures("unauthenticated")
    def must_be_authenticated(self):
        url = url_for('player.mute')
        response = self.client.delete(url)

        assert response.status_code == 401

    def should_fire_redis_unmute_event(self):
        url = url_for('player.mute')
        response = self.client.delete(url)

        assert response.status_code == 204
        self.redis.publish.assert_called_once_with(
            self.app.config.get('PLAYER_CHANNEL'),
            json.dumps({
                'event': 'set_mute',
                'mute': False
            }))
