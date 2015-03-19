#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_pause
=============================

Unit tests for the ``fm.views.player.PauseView`` class.
"""

import json
import mock

from flask import g, url_for
from fm.ext import db
from tests.factories.user import UserFactory


class BasePauseTest(object):

    def setup(self):
        # Patch Redis
        patch = mock.patch('fm.views.player.redis')
        self.redis = patch.start()
        self.addPatchCleanup(patch)

        # Fake User
        self.user = UserFactory()
        db.session.add(self.user)
        db.session.commit()
        g.user = self.user


class TestPausePost(BasePauseTest):

    def must_be_authenticated(self):
        del g.user

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


class TestPauseDelete(BasePauseTest):

    def must_be_authenticated(self):
        del g.user

        url = url_for('player.pause')
        response = self.client.delete(url)

        assert response.status_code == 401

    def should_fire_resume_event(self):
        url = url_for('player.pause')
        response = self.client.delete(url)

        assert response.status_code == 204
        self.redis.publish.assert_called_once_with(
            self.app.config.get('PLAYER_CHANNEL'),
            json.dumps({
                'event': 'resume',
            }))
