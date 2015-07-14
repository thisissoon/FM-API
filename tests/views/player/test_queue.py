#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_queue
=============================

Unit tests for the ``fm.views.player.QueueView`` class.
"""

# Standard Libs
import json
import uuid

# Third Party Libs
import httplib
import mock
import pytest
from flask import url_for
from mockredis import mock_redis_client
from tests import ALBUM_DATA, ALBUM_TRACKS_DATA, TRACK_DATA
from tests.factories.spotify import TrackFactory
from tests.factories.user import UserFactory

# First Party Libs
from fm.ext import config, db
from fm.models.spotify import Artist
from fm.models.user import User
from fm.serializers.spotify import TrackSerializer
from fm.serializers.user import UserSerializer
from fm.session import current_user


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
                    'user': users[i].id,
                    'uuid': '16fd2706-8baf-433b-82eb-8c7fada847da',
                })
            )
            expected.append({
                'track': TrackSerializer().serialize(track),
                'user': UserSerializer().serialize(users[i]),
                'uuid': '16fd2706-8baf-433b-82eb-8c7fada847da',
            })

        url = url_for('player.queue')
        response = self.client.get(url)

        assert response.status_code == 200
        assert expected == response.json


@pytest.mark.usefixtures("authenticated")
class TestQueuePost(QueueTest):

    def setup(self):
        super(TestQueuePost, self).setup()
        self.patch = mock.patch('requests.get')
        self.requests_mock = self.patch.start()
        self.addPatchCleanup(self.patch)

    def tearDown(self):
        self.requests_mock.stop()

    @pytest.mark.usefixtures("unauthenticated")
    def must_be_authenticated(self):
        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'uri': 'foo'
        }))

        assert response.status_code == httplib.UNAUTHORIZED

    def must_catch_validation_errors_for_non_existing_spotify_item(self):
        self.requests_mock.return_value = mock.MagicMock(
            status_code=httplib.NOT_FOUND
        )

        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'uri': 'spotify:track:foo'
        }))

        assert response.status_code == httplib.UNPROCESSABLE_ENTITY
        assert response.json['errors']['uri'][0]  \
            == 'Track not found on Spotify: spotify:track:foo'

    def must_catch_validation_errors_for_wront_spotify_uri(self):
        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({'uri': 'foo'}))

        assert response.status_code == httplib.UNPROCESSABLE_ENTITY
        assert response.json['errors']['uri'][0]  \
            == 'Unknow spotify uri: foo'

    @mock.patch('fm.tasks.queue.update_genres')
    def should_add_track_to_queue(self, update_genres):
        self.requests_mock.return_value = mock.MagicMock(
            status_code=httplib.OK,
            json=mock.MagicMock(return_value=TRACK_DATA)
        )

        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'uri': 'spotify:track:foo'
        }))

        queue = self.redis.get(config.PLAYLIST_REDIS_KEY)
        user = User.query.one()

        assert response.status_code == httplib.CREATED, response.data
        assert len(queue) == 1
        assert json.loads(queue[0])['user'] == user.id
        assert json.loads(queue[0])['uri'] == TRACK_DATA['uri']
        assert self.redis.publish.caled_once_with(json.dumps({
            'event': 'add',
            'uri': TRACK_DATA['uri'],
            'user': user.id
        }))
        update_genres.s.assert_called_with(Artist.query.all()[0].id)

    def should_add_album_tracks(self):
        mock_data = {
            'https://api.spotify.com/v1/albums/6akEvsycLGftJxYudPjmqK':
                mock.MagicMock(
                    status_code=httplib.OK,
                    json=mock.MagicMock(return_value=ALBUM_DATA)
                ),
            'https://api.spotify.com/v1/albums/6akEvsycLGftJxYudPjmqK/tracks':
                mock.MagicMock(
                    status_code=httplib.OK,
                    json=mock.MagicMock(return_value=ALBUM_TRACKS_DATA)
                ),
            'https://api.spotify.com/v1/tracks/2TpxZ7JUBn3uw46aR7qd6V':
                mock.MagicMock(
                    status_code=httplib.OK,
                    json=mock.MagicMock(return_value=TRACK_DATA)
                ),
            'https://api.spotify.com/v1/tracks/4PjcfyZZVE10TFd9EKA72r':
                mock.MagicMock(
                    status_code=httplib.OK,
                    json=mock.MagicMock(return_value=TRACK_DATA)
                ),
        }
        self.requests_mock.side_effect = lambda x, *args, **kwargs: mock_data.pop(x)

        url = url_for('player.queue')
        response = self.client.post(url, data=json.dumps({
            'uri': 'spotify:album:6akEvsycLGftJxYudPjmqK'
        }))

        queue = self.redis.get(config.PLAYLIST_REDIS_KEY)
        assert response.status_code == httplib.CREATED
        assert len(queue) == 2
        assert self.redis.publish.call_count == 1


@pytest.mark.usefixtures("authenticated")
class TestQueueDelete(QueueTest):

    @pytest.mark.usefixtures("unauthenticated")
    def must_be_authenticated(self):
        url = url_for('player.queue')
        response = self.client.delete(url, data=json.dumps({
            'uri': 'foo',
            'uuid': '16fd2706-8baf-433b-82eb-8c7fada847da',
        }))

        assert response.status_code == httplib.UNAUTHORIZED

    @pytest.mark.skipif(True, reason='Redis mock library is not fully compatible')
    def should_delete_track_in_queue(self):
        tracks = [TrackFactory() for i in range(3)]
        db.session.add_all(tracks)
        db.session.commit()

        for i, track in enumerate(tracks):
            track_uuid = str(uuid.uuid4())
            self.redis.rpush(
                config.PLAYLIST_REDIS_KEY,
                json.dumps({
                    'uri': track.spotify_uri,
                    'user': current_user.id,
                    'uuid': track_uuid,
                })
            )

        url = url_for('player.queue', uuid=track_uuid)
        response = self.client.delete(url)
        assert response.status_code == httplib.OK
        assert self.redis.llen(config.PLAYLIST_REDIS_KEY) == 2

    def should_return_no_content_for_non_existing_key(self):
        TrackFactory.create()

        url = url_for('player.queue')
        url = url_for('player.queue', uuid='bla-bla-bla')
        response = self.client.delete(url)

        assert response.status_code == httplib.NO_CONTENT

    def should_publish_remove_event(self):
        track = TrackFactory.create()
        db.session.add(track)
        db.session.commit()

        self.redis.rpush(
            config.PLAYLIST_REDIS_KEY,
            json.dumps({
                'uri': track.spotify_uri,
                'user': current_user.id,
                'uuid': '16fd2706-8baf-433b-82eb-8c7fada847da',
            })
        )

        url = url_for('player.queue')
        url = url_for('player.queue', uuid='16fd2706-8baf-433b-82eb-8c7fada847da')
        response = self.client.delete(url)

        assert response.status_code == httplib.OK
        self.redis.publish.assert_called_once_with(
            config.PLAYER_CHANNEL,
            json.dumps({
                'event': 'deleted',
                'uri': track.spotify_uri,
                'user': current_user.id
            })
        )
