import unittest

import mock

from fm.ext import db
from fm.logic.player import Queue
from mockredis import mock_redis_client
from tests.factories.spotify import TrackFactory
from tests.factories.user import UserFactory


@mock.patch('fm.logic.player.redis', mock_redis_client())
class TestQueue(unittest.TestCase):

    def test_add_track_into_queue(self):
        track = TrackFactory()
        user = UserFactory()
        db.session.add_all([track, user])
        db.session.commit()

        Queue.add(track, user)
        assert Queue.length() == 1
