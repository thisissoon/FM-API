#!/usr/bin/env python
# encoding: utf-8

"""
tests.tasks.test_track
=======================

Unittests for Track Celery Tasks.
"""

# Standard Libs
import uuid

# Third Party Libs
import mock
from tests.factories.spotify import TrackFactory

# First Party Libs
from fm.ext import db
from fm.models.spotify import Track
from fm.tasks.track import update_analysis
from fm.thirdparty.echonest import EchoNestError


class TestUpdateAnalysis(object):

    def setup(self):
        patch = mock.patch('fm.tasks.track.get_track_analysis')
        self.get_track_analysis = patch.start()
        self.get_track_analysis.return_value = {}
        self.addPatchCleanup(patch)

    def should_return_false_track_not_found(self):
        result = update_analysis.delay(unicode(uuid.uuid4()))

        assert result.wait() is False

    def should_should_raise_exception_on_echonest_error(self):
        self.get_track_analysis.side_effect = EchoNestError

        t = TrackFactory()

        db.session.add(t)
        db.session.commit()

        result = update_analysis.delay(t.id)

        assert result.wait() is False
        self.get_track_analysis.assert_called_once_with(t.spotify_uri)

    def should_udpate_track_analysis(self):

        self.get_track_analysis.return_value = {'danceability': 0.5164314670162907}

        t = TrackFactory()

        db.session.add(t)
        db.session.commit()

        result = update_analysis.delay(t.id)
        track = Track.query.all()[0]

        assert result.wait() is True
        assert track.audio_summary['danceability'] == 0.5164314670162907
        self.get_track_analysis.assert_called_once_with(track.spotify_uri)
