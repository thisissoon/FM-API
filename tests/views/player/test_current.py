#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_current
===============================

Unit tests for the ``fm.views.player.CurrentView`` class.
"""

import mock

from fm.ext import db
from fm.serializers.spotify import TrackSerialzier
from flask import url_for
from tests.factories.spotify import TrackFactory


class BaseCurrentTest(object):

    def setup(self):
        patch = mock.patch('fm.views.player.redis')
        self.redis = patch.start()
        self.addPatchCleanup(patch)


class TestCurrentGet(BaseCurrentTest):

    def should_return_no_content_if_no_data_in_redis(self):
        self.redis.get.return_value = None

        url = url_for('player.current')
        response = self.client.get(url)

        assert response.status_code == 204

    def should_return_no_content_if_track_not_in_db(self):
        self.redis.get.return_value = 'spotify:track:foo'

        url = url_for('player.current')
        response = self.client.get(url)

        assert response.status_code == 204

    def should_return_track_data(self):
        track = TrackFactory()

        db.session.add(track)
        db.session.commit()

        self.redis.get.return_value = track.spotify_uri

        url = url_for('player.current')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json == TrackSerialzier().serialize(track)
