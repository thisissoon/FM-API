#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_queue_meta
=============================

Unit tests for the ``fm.views.player.QueueMetaView`` class.
"""

# Standard Libs
# import httplib
import json

# Third Pary Libs
import mock
# import pytest
# import requests
from flask import url_for
from mockredis import mock_redis_client

# First Party Libs
from fm.ext import config, db
# from fm.models.spotify import Artist
# from fm.models.user import User
# from fm.serializers.spotify import TrackSerializer
# from fm.serializers.user import UserSerializer
# from tests import TRACK_DATA
from tests.factories.spotify import TrackFactory
# from tests.factories.user import UserFactory


class TestQueueMeta(object):

    def setup(self):
        # Standard redis mock client to be used across multiple patches
        self.redis = mock_redis_client()
        self.redis.publish = mock.MagicMock()

        # Patch redis in the player logic module
        patch = mock.patch(
            'fm.logic.player.redis',
            new_callable=mock.PropertyMock(return_value=self.redis))
        patch.start()
        self.addPatchCleanup(patch)

        # Patch redis in the player views module
        patch = mock.patch(
            'fm.views.player.redis',
            new_callable=mock.PropertyMock(return_value=self.redis))
        patch.start()
        self.addPatchCleanup(patch)

    def should_return_total_played_time_of_all_tracks_in_queue(self):
        tracks = TrackFactory.create_batch(3) * 2  # add some duplicates
        db.session.add_all(tracks + TrackFactory.create_batch(2))
        db.session.commit()

        for track in tracks:
            self.redis.rpush(
                config.PLAYLIST_REDIS_KEY,
                json.dumps({
                    'uri': track.spotify_uri,
                    'user': 'user'
                })
            )

        url = url_for('player.queue-meta')
        response = self.client.get(url)

        assert response.status_code == 200
        assert sum(t.duration for t in tracks) == response.json['play_time']

    def should_total_number_in_queue(self):
        tracks = TrackFactory.create_batch(3)
        db.session.add_all(tracks)
        db.session.commit()

        for track in tracks:
            self.redis.rpush(
                config.PLAYLIST_REDIS_KEY,
                json.dumps({
                    'uri': track.spotify_uri,
                    'user': 'user'
                })
            )

        url = url_for('player.queue-meta')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total'] == 3
