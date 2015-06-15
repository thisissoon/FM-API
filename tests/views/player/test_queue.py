#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_queue
=============================

Unit tests for the ``fm.views.player.QueueView`` class.
"""

# Standard Libs
import json

# Third Pary Libs
import httplib
import mock
import pytest
import requests
from flask import url_for
from mockredis import mock_redis_client
from tests import TRACK_DATA
from tests.factories.spotify import TrackFactory
from tests.factories.user import UserFactory

# First Party Libs
from fm.ext import config, db
from fm.models.spotify import Artist
from fm.models.user import User
from fm.serializers.spotify import TrackSerializer
from fm.serializers.user import UserSerializer


class QueueTest(object):

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


class TestGetQueue(QueueTest):

    def ensure_same_track_is_not_grouped(self):
        track = TrackFactory()
        user = UserFactory()

        db.session.add_all([track, user])
        db.session.commit()

        # Add the track 3 times to the queue - we should get it 3 times
        for i in range(3):
            self.redis.rpush(
                config.PLAYLIST_REDIS_KEY,
                json.dumps({
                    'uri': track.spotify_uri,
                    'user': user.id
                })
            )

        url = url_for('player.queue')
        response = self.client.get(url)

        assert response.status_code == 200
        assert len(response.json) == 3

    def must_return_empty_list_when_no_queue(self):
        url = url_for('player.queue')
        response = self.client.get(url)

        assert response.status_code == 200
        assert len(response.json) == 0

    def should_return_200_ok(self):
        tracks = [TrackFactory() for i in range(3)]
        users = [UserFactory() for i in range(3)]

        db.session.add_all(tracks + users)
        db.session.commit()

        expected = []
        for i, track in enumerate(tracks):
            self.redis.rpush(
                config.PLAYLIST_REDIS_KEY,
                json.dumps({
                    'uri': track.spotify_uri,
                    'user': users[i].id
                })
            )
            expected.append({
                'track': TrackSerializer().serialize(track),
                'user': UserSerializer().serialize(users[i])
            })

        url = url_for('player.queue')
        response = self.client.get(url)

        assert response.status_code == 200
        assert expected == response.json


@pytest.mark.usefixtures("authenticated")
class TestQueuePost(QueueTest):

    def setup(self):
        super(TestQueuePost, self).setup()

        # Patch Requests to Spotify
        self.requests = mock.MagicMock()
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(return_value=TRACK_DATA))
        self.requests.ConnectionError = requests.ConnectionError

        patch = mock.patch(
            'fm.serializers.types.spotify.requests',
            new_callable=mock.PropertyMock(return_value=self.requests))

        patch.start()
        self.addPatchCleanup(patch)

    @pytest.mark.usefixtures("unauthenticated")
    def must_be_authenticated(self):
        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'uri': 'foo'
        }))

        assert response.status_code == httplib.UNAUTHORIZED

    def must_catch_validation_errors(self):
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.NOT_FOUND)

        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'uri': 'spotify:track:foo'
        }))

        assert response.status_code == httplib.UNPROCESSABLE_ENTITY
        assert response.json['errors']['uri'][0]  \
            == 'Track not found on Spotify: spotify:track:foo'

    @mock.patch('fm.tasks.queue.update_genres')
    def should_add_track_to_queue(self, update_genres):
        self.requests.get.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(return_value=TRACK_DATA))

        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'uri': 'spotify:track:foo'
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
        update_genres.s.assert_called_with(Artist.query.all()[0].id)
