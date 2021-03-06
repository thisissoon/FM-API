# Standard Libs
import unittest

# Third Party Libs
from tests.factories.spotify import TrackFactory

# First Party Libs
from fm.ext import db
from fm.logic.player import Random


class TestQueue(unittest.TestCase):

    def test_add_track_into_queue(self):
        tracks = [TrackFactory(), TrackFactory(), TrackFactory()]
        db.session.add_all(tracks)
        db.session.commit()

        random_tracks = Random.get_tracks(count=3)
        assert set(random_tracks) == set(tracks)
