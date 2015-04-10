#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_queue
=============================

Unit tests for the ``fm.views.player.QueueView`` class.
"""

import httplib
import json
import mock
import pytest
import requests

from fm.ext import config, db
from fm.models.user import User
from fm.serializers.spotify import TrackSerializer
from fm.serializers.user import UserSerializer
from flask import url_for
from mockredis import mock_redis_client
from tests import TRACK_DATA
from tests.factories.spotify import TrackFactory
from tests.factories.user import UserFactory


class QueueTest(object):

    def setup(self):
        patch = mock.patch('fm.views.player.redis')
        self.redis = patch.start()
        self.addPatchCleanup(patch)


class TestGetQueue(QueueTest):

    def ensure_same_track_is_not_grouped(self):
        tracks = [TrackFactory(), TrackFactory(), TrackFactory()]
        users = [UserFactory(), UserFactory(), UserFactory()]

        db.session.add_all(tracks + users)
        db.session.commit()

        # Each track is in the queue twice
        queue = []
        for i, t in enumerate(tracks):
            queue.append(json.dumps({
                'uri': t.spotify_uri,
                'user': users[i].id
            }))

        queue = queue + queue

        self.redis.lrange.return_value = queue
        self.redis.llen.return_value = len(tracks)

        url = url_for('player.queue')
        response = self.client.get(url)

        assert response.status_code == 200
        assert len(response.json) == 6

    def must_return_empty_list_when_no_queue(self):
        self.redis.lrange.return_value = []
        self.redis.llen.return_value = 0

        url = url_for('player.queue')
        response = self.client.get(url)

        assert response.status_code == 200
        assert len(response.json) == 0

    def should_return_200_ok(self):
        tracks = [TrackFactory(), TrackFactory(), TrackFactory()]
        users = [UserFactory(), UserFactory(), UserFactory()]

        db.session.add_all(tracks + users)
        db.session.commit()

        # Each track is in the queue twice
        queue = []
        for i, t in enumerate(tracks):
            queue.append(json.dumps({
                'uri': t.spotify_uri,
                'user': users[i].id
            }))

        self.redis.lrange.return_value = queue
        self.redis.llen.return_value = len(tracks)

        url = url_for('player.queue')
        response = self.client.get(url)

        expected = []
        for i, track in enumerate(tracks):
            user = users[i]
            expected.append({
                'track': TrackSerializer().serialize(track),
                'user': UserSerializer().serialize(user)
            })

        assert response.status_code == 200
        assert expected == response.json


@pytest.mark.usefixtures("authenticated")
class TestQueuePost(QueueTest):

    def setup(self):
        super(TestQueuePost, self).setup()

        self.requests = mock.MagicMock()
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(return_value=TRACK_DATA))
        self.requests.ConnectionError = requests.ConnectionError

        # Patch Requests to Spotify
        patch = mock.patch(
            'fm.serializers.types.spotify.requests',
            new_callable=mock.PropertyMock(return_value=self.requests))

        patch.start()
        self.addPatchCleanup(patch)

        patch = mock.patch('fm.logic.player.redis', mock_redis_client())
        self.redis = patch.start()
        self.redis.publish = mock.MagicMock()
        self.addPatchCleanup(patch)

    @pytest.mark.usefixtures("unauthenticated")
    def must_be_authenticated(self):
        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'track': 'foo'
        }))

        assert response.status_code == httplib.UNAUTHORIZED

    def should_call_queue_add_task(self):
        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'track': 'spotify:track:foo'
        }))

        queue = self.redis.get(config.PLAYLIST_REDIS_KEY)
        user = User.query.one()

        assert response.status_code == httplib.CREATED
        assert len(queue) == 1
        assert json.loads(queue[0])['user'] == user.id
        assert json.loads(queue[0])['uri'] == TRACK_DATA['uri']
        assert self.redis.publish.caled_once_with(json.dumps({
            'event': 'add',
            'uri': TRACK_DATA['uri'],
            'user': user.id
        }))
