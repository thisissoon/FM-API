#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_queue
=============================

Unit tests for the ``fm.views.player.QueueView`` class.
"""

import mock

from fm.ext import db
from fm.serializers.spotify import TrackSerialzier
from flask import url_for
from tests.factories.spotify import TrackFactory


class TestGetQueue(object):

    def setup(self):
        patch = mock.patch('fm.views.player.redis')
        self.redis = patch.start()
        self.addPatchCleanup(patch)

    def ensure_same_track_is_not_grouped(self):
        tracks = [TrackFactory(), TrackFactory(), TrackFactory()]

        db.session.add_all(tracks)
        db.session.commit()

        # Each track is in the queue twice
        queue = [t.spotify_uri for t in tracks] + [t.spotify_uri for t in tracks]

        self.redis.lrange.return_value = queue
        self.redis.llen.return_value = len(tracks)

        url = url_for('player.queue')
        response = self.client.get(url)

        assert len(response.json) == 6

    def must_return_empty_list_when_no_queue(self):
        self.redis.lrange.return_value = []
        self.redis.llen.return_value = 0

        url = url_for('player.queue')
        response = self.client.get(url)

        assert len(response.json) == 0

    def should_return_200_ok(self):
        tracks = [TrackFactory(), TrackFactory(), TrackFactory()]

        db.session.add_all(tracks)
        db.session.commit()

        # Each track is in the queue twice
        queue = [t.spotify_uri for t in tracks]

        self.redis.lrange.return_value = queue
        self.redis.llen.return_value = len(tracks)

        url = url_for('player.queue')
        response = self.client.get(url)

        expected = TrackSerialzier().serialize(tracks, many=True)

        assert response.status_code == 200
        assert expected == response.json
