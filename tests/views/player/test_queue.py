#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_queue
=============================

Unit tests for the ``fm.views.player.QueueView`` class.
"""

import mock

from fm.ext import db
from flask import url_for
from tests.factories.spotify import TrackFactory


class TestGetQueue(object):
    """Player Queue: GET
    """

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
