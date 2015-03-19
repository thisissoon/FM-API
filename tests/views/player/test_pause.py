#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_pause
=============================

Unit tests for the ``fm.views.player.PauseView`` class.
"""

import json
import mock

from flask import url_for


class BasePauseTest(object):

    def setup(self):
        patch = mock.patch('fm.views.player.redis')
        self.redis = patch.start()
        self.addPatchCleanup(patch)


class TestPausePost(BasePauseTest):

    def should_fire_pause_event(self):
        url = url_for('player.pause')
        response = self.client.post(url)

        assert response.status_code == 201
        self.redis.publish.assert_called_once_with(
            self.app.config.get('PLAYER_CHANNEL'),
            json.dumps({
                'event': 'pause',
            }))


class TestPauseDelete(BasePauseTest):

    def should_fire_resume_event(self):
        url = url_for('player.pause')
        response = self.client.delete(url)

        assert response.status_code == 204
        self.redis.publish.assert_called_once_with(
            self.app.config.get('PLAYER_CHANNEL'),
            json.dumps({
                'event': 'resume',
            }))
