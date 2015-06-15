#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_history
===============================

Unit tests for the ``fm.views.player.HistoryView`` class.
"""

# Standard Libs
import datetime

# Third Pary Libs
from dateutil.tz import tzutc
from flask import url_for
from tests.factories.spotify import PlaylistHistoryFactory

# First Party Libs
from fm.ext import db


class TestGetHistory(object):

    def should_return_latest_entries(self):
        entries = [
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 12, 12, 15, tzinfo=tzutc())),
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 12, 12, 15, 12, tzinfo=tzutc())),
        ]

        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.history')
        response = self.client.get(url)

        assert response.status_code == 200
        assert len(response.json) == 2
        assert entries[0].track.id == response.json[1]['track']['id']
        assert entries[1].track.id == response.json[0]['track']['id']
