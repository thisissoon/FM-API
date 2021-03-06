# Standard Libs
import unittest

# Third Party Libs
import mock
from mockredis import mock_redis_client
from tests.factories.spotify import TrackFactory
from tests.factories.user import UserFactory

# First Party Libs
from fm.ext import db
from fm.logic.player import Queue


@mock.patch('fm.logic.player.redis', mock_redis_client())
class TestQueue(unittest.TestCase):

    def test_add_track_into_queue(self):
        track = TrackFactory()
        user = UserFactory()
        db.session.add_all([track, user])
        db.session.commit()

        Queue.add(track.spotify_uri, user.id)
        assert Queue.length() == 1
