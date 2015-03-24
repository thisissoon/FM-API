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

from fm.ext import db
from fm.views.player import CurrentView
from fm.serializers.spotify import TrackSerialzier
from flask import url_for
from tests.factories.spotify import TrackFactory


class BaseCurrentTest(object):

    def setup(self):
        patch = mock.patch('fm.views.player.redis')
        self.redis = patch.start()
        self.addPatchCleanup(patch)


class TestGetCurrentTrack(BaseCurrentTest):

    def should_return_none_no_current_track_in_redis(self):
        self.redis.get.return_value = None

        assert CurrentView().get_current_track() is None

    def should_return_no_content_if_track_not_in_db(self):
        self.redis.get.return_value = 'spotify:track:foo'

        assert CurrentView().get_current_track() is None

    def should_return_track_instance(self):
        track = TrackFactory()

        db.session.add(track)
        db.session.commit()

        self.redis.get.return_value = track.spotify_uri

        assert CurrentView().get_current_track().id == track.id


class TestCurrentGet(BaseCurrentTest):

    def should_return_track_data(self):
        track = TrackFactory()

        db.session.add(track)
        db.session.commit()

        self.redis.get.return_value = track.spotify_uri

        url = url_for('player.current')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json == TrackSerialzier().serialize(track)


@pytest.mark.usefixtures("authenticated")
class TestCurrentDelete(BaseCurrentTest):

    @pytest.mark.usefixtures("unauthenticated")
    def must_be_authenticated(self):
        url = url_for('player.mute')
        response = self.client.delete(url)

        assert response.status_code == 401

    def should_fire_stop_event(self):
        track = TrackFactory()

        db.session.add(track)
        db.session.commit()

        self.redis.get.return_value = track.spotify_uri

        url = url_for('player.current')
        response = self.client.delete(url)

        assert response.status_code == 204
        self.redis.publish.assert_called_once_with(
            self.app.config.get('PLAYER_CHANNEL'),
            json.dumps({
                'event': 'stop'
            })
        )
