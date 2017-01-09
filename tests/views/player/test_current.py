#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_current
===============================

Unit tests for the ``fm.views.player.CurrentView`` class.
"""

# Standard Libs
import datetime
import json
import uuid

# Third Party Libs
import dateutil.tz
import mock
import pytest
from flask import url_for
from tests.factories.spotify import TrackFactory
from tests.factories.user import UserFactory

# First Party Libs
from fm.ext import db
from fm.serializers.spotify import TrackSerializer
from fm.serializers.user import UserSerializer
from fm.views.player import CurrentView


class BaseCurrentTest(object):

    def setup(self):
        patch = mock.patch('fm.views.player.redis')
        self.redis = patch.start()
        self.addPatchCleanup(patch)


class TestGetCurrentTrack(BaseCurrentTest):

    def should_return_none_no_current_track_in_redis(self):
        self.redis.get.return_value = None

        assert CurrentView().get_current_track() == (None, None)

    def should_return_no_content_if_track_not_in_db(self):
        self.redis.get.return_value = json.dumps({
            'uri': 'spotify:track:foo',
            'user': unicode(uuid.uuid4())
        })

        assert CurrentView().get_current_track() == (None, None)

    def should_return_track_instance(self):
        track = TrackFactory()
        user = UserFactory()

        db.session.add_all([track, user])
        db.session.commit()

        self.redis.get.return_value = json.dumps({
            'uri': track.spotify_uri,
            'user': user.id
        })

        assert CurrentView().get_current_track() == (track, user)


class TestCalculateElapsed(BaseCurrentTest):

    def test_no_start_time_set_uses_now(self):
        now = datetime.datetime(2015, 1, 1, 12, 13, 14)
        self.redis.get.return_value = None

        with mock.patch('fm.views.player.datetime') as _dt:
            _dt.utcnow.return_value = now
            assert CurrentView().elapsed() == 0

    def test_no_paused_durration(self):
        tzutc = dateutil.tz.tzutc()
        now = datetime.datetime(2015, 1, 1, 13, 10, 2, tzinfo=tzutc)
        # Started 2 seconds ago
        start_time = datetime.datetime(2015, 1, 1, 13, 10, 0, tzinfo=tzutc)

        self.redis.get.return_value = start_time.isoformat()

        with mock.patch('fm.views.player.datetime') as _dt:
            _dt.utcnow.return_value = now

            # No pauses, 2 seconds of play
            assert CurrentView().elapsed() == 2000

    def test_with_pause_durration(self):
        tzutc = dateutil.tz.tzutc()
        now = datetime.datetime(2015, 1, 1, 13, 10, 23, tzinfo=tzutc)  # now
        # started 22 seconds ago
        start_time = datetime.datetime(2015, 1, 1, 13, 10, 0, tzinfo=tzutc)

        # Paused for 20 seconds = 20000 ms
        self.redis.get.side_effect = [
            start_time.isoformat(),
            20000,  # Paused for 20 seconds
        ]

        with mock.patch('fm.views.player.datetime') as _dt:
            _dt.utcnow.return_value = now

            # We should have 3 seconds of total play
            assert CurrentView().elapsed() == 3000

    def test_in_live_pause_state(self):
        tzutc = dateutil.tz.tzutc()
        now = datetime.datetime(2015, 1, 1, 13, 10, 32, tzinfo=tzutc)
        # started 32 seconds ago
        start_time = datetime.datetime(2015, 1, 1, 13, 10, 0, tzinfo=tzutc)
        # 3 seconds of play
        pause_start = datetime.datetime(2015, 1, 1, 13, 10, 23, tzinfo=tzutc)

        # Paused for 20 seconds = 20000 ms
        self.redis.get.side_effect = [
            start_time.isoformat(),
            20000,  # 20 seconds of first pause
            pause_start.isoformat(),  # paused 2 secs later
        ]

        with mock.patch('fm.views.player.datetime') as _dt:
            _dt.utcnow.return_value = now

            # We should have 3 seconds of total play
            assert CurrentView().elapsed(paused=True) == 3000


class TestCurrentGet(BaseCurrentTest):

    def should_return_track_data(self):
        track = TrackFactory(duration=10000)
        user = UserFactory()

        db.session.add_all([track, user])
        db.session.commit()

        now = datetime.datetime.utcnow()
        start = now - datetime.timedelta(seconds=5)
        start = start.replace(tzinfo=dateutil.tz.tzutc())

        mock_redis_values = {
            'fm:player:current': json.dumps({
                'uri': track.spotify_uri,
                'user': user.id
            }),
            'fm:player:start_time': start.isoformat()
        }
        self.redis.get.side_effect = lambda x: mock_redis_values.get(x)

        url = url_for('player.current')

        # We have to mock utcnow so we don't get drift in the test
        with mock.patch('fm.views.player.datetime') as _dt:
            _dt.utcnow.return_value = now
            response = self.client.get(url)

        assert response.status_code == 200, response.json
        assert response.json['track'] == TrackSerializer().serialize(track)
        assert response.json['user'] == UserSerializer().serialize(user)
        assert response.json['player']['elapsed_time'] == 5000
        assert response.json['player']['elapsed_percentage'] == 50
        assert response.json['player']['elapsed_seconds'] == 5

    def should_return_zero_when_elapsed_time_cant_be_pulled(self):
        track = TrackFactory()
        user = UserFactory()

        db.session.add_all([track, user])
        db.session.commit()

        mock_redis_values = {
            'fm:player:current': json.dumps({
                'uri': track.spotify_uri,
                'user': user.id
            }),
            'fm:player:elapsed_time': None
        }
        self.redis.get.side_effect = lambda x: mock_redis_values.get(x)

        url = url_for('player.current')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['track'] == TrackSerializer().serialize(track)
        assert response.json['user'] == UserSerializer().serialize(user)
        assert response.json['player']['elapsed_time'] == 0
        assert response.json['player']['elapsed_percentage'] == 0
        assert response.json['player']['elapsed_seconds'] == 0


@pytest.mark.usefixtures("authenticated")
class TestCurrentDelete(BaseCurrentTest):

    @pytest.mark.usefixtures("unauthenticated")
    def must_be_authenticated(self):
        url = url_for('player.mute')
        response = self.client.delete(url)

        assert response.status_code == 401

    def should_fire_stop_event(self):
        track = TrackFactory()
        user = UserFactory()

        db.session.add_all([track, user])
        db.session.commit()

        self.redis.get.return_value = json.dumps({
            'uri': track.spotify_uri,
            'user': user.id
        })

        url = url_for('player.current')
        response = self.client.delete(url)

        assert response.status_code == 200
        self.redis.publish.assert_called_once_with(
            self.app.config.get('PLAYER_CHANNEL'),
            json.dumps({
                'event': 'stop',
                'user': str(user.id),
                'track': str(track.id),
            })
        )
