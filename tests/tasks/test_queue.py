#!/usr/bin/env python
# encoding: utf-8

"""
tests.tasks.test_queue
======================

Unit Tests for Celery Queue Tasks
"""

import mock

from fm.ext import db
from fm.models.spotify import Album
from mockredis import mock_redis_client
from tests import TRACK_DATA
from tests.factories.spotify import AlbumFactory
from tests.factories.user import UserFactory

from fm.tasks.queue import add


@mock.patch('fm.logic.player.redis', mock_redis_client())
class TestAdd(object):

    def should_update_existing_album(self):
        user = UserFactory()
        album = AlbumFactory(spotify_uri=TRACK_DATA['album']['uri'])

        db.session.add_all([user, album])
        db.session.commit()

        add.delay(TRACK_DATA, user.id)

        assert Album.query.count() == 1
        assert Album.query.first().name == TRACK_DATA['album']['name']
