#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_random
===============================

Unit tests for the ``fm.views.player.RandomView`` class.
"""

import httplib
import json

import mock

import pytest
from flask import url_for
from fm.ext import db
from fm.logic.player import Queue
from mockredis import mock_redis_client
from tests.factories.spotify import TrackFactory
from tests.factories.user import UserFactory


@pytest.mark.usefixtures("authenticated")
class TestRandom(object):

    @pytest.mark.usefixtures("unauthenticated")
    def test_hit_random_endpoint_as_unauthorized_user(self):
        response = self.client.post(url_for('player.random'))
        assert response.status_code == httplib.UNAUTHORIZED

    def test_data_without_number_of_tracks(self):
        response = self.client.post(url_for('player.random'))
        assert response.status_code == httplib.BAD_REQUEST

    @mock.patch('fm.logic.player.redis', mock_redis_client())
    def test_add_some_tracks_into_queue(self):
        tracks = [TrackFactory(), TrackFactory(), TrackFactory()]
        users = [UserFactory(), UserFactory(), UserFactory()]

        db.session.add_all(tracks + users)
        db.session.commit()

        response = self.client.post(
            url_for('player.random'),
            data=json.dumps({'tracks': 2})
        )

        assert response.status_code == httplib.CREATED
        assert Queue.length() == 2
