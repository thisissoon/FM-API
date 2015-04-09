#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_queue
=============================

Unit tests for the ``fm.views.player.QueueView`` class.
"""

import json
import mock
import pytest
import requests

from fm.ext import db
from fm.models.spotify import Album, Artist, Track
from fm.serializers.spotify import TrackSerializer
from fm.serializers.user import UserSerializer
from flask import url_for
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
            status_code=200,
            json=mock.MagicMock(return_value=TRACK_DATA))
        self.requests.ConnectionError = requests.ConnectionError

        # Patch Requests to Spotify
        patch = mock.patch(
            'fm.serializers.types.spotify.requests',
            new_callable=mock.PropertyMock(return_value=self.requests))

        patch.start()

        self.addPatchCleanup(patch)

        patch = mock.patch('fm.views.player.Queue')
        patch.start()
        self.addPatchCleanup(patch)

    @pytest.mark.usefixtures("unauthenticated")
    def must_be_authenticated(self):
        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'track': 'foo'
        }))

        assert response.status_code == 401

    def should_catch_connection_error(self):
        self.requests.get.side_effect = requests.ConnectionError()

        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'track': 'foo'
        }))

        assert response.status_code == 422
        assert 'Unable to get track data from Spotify' in response.json['errors']['track']

    def ensure_valid_spotify_uri(self):
        self.requests.get.return_value = mock.MagicMock(status_code=404)

        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'track': 'foo'
        }))

        assert response.status_code == 422
        assert 'Invalid Spotify URI: foo' in response.json['errors']['track']

    def should_create_new_album(self):
        assert Album.query.count() == 0

        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'track': 'foo'
        }))

        album = Album.query.first()

        assert response.status_code == 201
        assert album is not None
        assert album.name == TRACK_DATA['album']['name']
        assert album.images == TRACK_DATA['album']['images']
        assert album.spotify_uri == TRACK_DATA['album']['uri']

    def should_create_artist(self):
        assert Artist.query.count() == 0

        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'track': 'foo'
        }))

        artist = Artist.query.first()

        assert response.status_code == 201
        assert artist is not None
        assert artist.name == TRACK_DATA['artists'][0]['name']
        assert artist.spotify_uri == TRACK_DATA['artists'][0]['uri']

    def ensure_new_track_play_count_is_one(self):
        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'track': 'foo'
        }))

        track = Track.query.first()

        assert response.status_code == 201
        assert track.play_count == 1

    def should_increment_existing_track_play_count(self):
        t = TrackFactory(spotify_uri=TRACK_DATA['uri'], play_count=5)

        db.session.add(t)
        db.session.commit()

        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'track': t.spotify_uri
        }))

        track = Track.query.first()

        assert response.status_code == 201
        assert track.play_count == 6
