#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_current
===============================

Unit tests for the ``fm.views.player.CurrentView`` class.
"""

import json
import mock
import pytest
import uuid

from fm.ext import db
from fm.views.player import CurrentView
from fm.serializers.spotify import TrackSerializer
from fm.serializers.user import UserSerializer
from flask import url_for
from tests.factories.spotify import TrackFactory
from tests.factories.user import UserFactory


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


class TestCurrentGet(BaseCurrentTest):

    def should_return_track_data(self):
        track = TrackFactory()
        user = UserFactory()

        db.session.add_all([track, user])
        db.session.commit()

        self.redis.get.return_value = json.dumps({
            'uri': track.spotify_uri,
            'user': user.id
        })

        url = url_for('player.current')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['track'] == TrackSerializer().serialize(track)
        assert response.json['user'] == UserSerializer().serialize(user)


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

        assert response.status_code == 204
        self.redis.publish.assert_called_once_with(
            self.app.config.get('PLAYER_CHANNEL'),
            json.dumps({
                'event': 'stop'
            })
        )
