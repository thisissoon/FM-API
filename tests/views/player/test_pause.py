#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_pause
=============================

Unit tests for the ``fm.views.player.PauseView`` class.
"""

# Standard Libs
import json

# Third Pary Libs
import mock
import pytest
from flask import url_for


class BasePauseTest(object):

    def setup(self):
        # Patch Redis
        patch = mock.patch('fm.views.player.redis')
        self.redis = patch.start()
        self.addPatchCleanup(patch)


@pytest.mark.usefixtures("authenticated")
class TestPausePost(BasePauseTest):

    @pytest.mark.usefixtures("unauthenticated")
    def must_be_authenticated(self):
        url = url_for('player.pause')
        response = self.client.post(url)

        assert response.status_code == 401

    def should_fire_pause_event(self):
        url = url_for('player.pause')
        response = self.client.post(url)

        assert response.status_code == 201
        self.redis.publish.assert_called_once_with(
            self.app.config.get('PLAYER_CHANNEL'),
            json.dumps({
                'event': 'pause',
            }))


@pytest.mark.usefixtures("authenticated")
class TestPauseDelete(BasePauseTest):

    @pytest.mark.usefixtures("unauthenticated")
    def must_be_authenticated(self):
        url = url_for('player.pause')
        response = self.client.delete(url)

        assert response.status_code == 401

    def should_fire_resume_event(self):
        url = url_for('player.pause')
        response = self.client.delete(url)

        assert response.status_code == 200
        self.redis.publish.assert_called_once_with(
            self.app.config.get('PLAYER_CHANNEL'),
            json.dumps({
                'event': 'resume',
            }))
