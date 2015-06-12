#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_stats
===============================

Unit tests for the ``fm.views.player.StatsView`` class.
"""
# Standard Libs
import datetime

# Third Party Libs
from dateutil.tz import tzutc
from flask import url_for
from tests.factories.spotify import (
    AlbumWithArtist,
    ArtistFactory,
    PlaylistHistoryFactory,
    TrackFactory,
    UserFactory
)

# First Party Libs
from fm.ext import db
from fm.serializers.spotify import ArtistSerializer, TrackSerializer
from fm.serializers.user import UserSerializer


class TestGetStats(object):

    def should_return_most_played_djs_since_selected_date(self):
        most_played = UserFactory()
        second_most_played = UserFactory()
        entries = [
            PlaylistHistoryFactory(user=most_played),
            PlaylistHistoryFactory(user=most_played),
            PlaylistHistoryFactory(user=second_most_played),
            PlaylistHistoryFactory(
                user=second_most_played,
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc())
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', since='2015-06-01')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_active_djs'] == [
            {
                'user': UserSerializer().serialize(most_played),
                'total': 2
            },
            {
                'user': UserSerializer().serialize(second_most_played),
                'total': 1
            },
        ]

    def should_return_most_played_djs_from_the_beginning_of_the_world(self):
        most_played = UserFactory()
        second_most_played = UserFactory()
        entries = [
            PlaylistHistoryFactory(user=most_played),
            PlaylistHistoryFactory(user=most_played),
            PlaylistHistoryFactory(user=second_most_played),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_active_djs'] == [
            {
                'user': UserSerializer().serialize(most_played),
                'total': 2
            },
            {
                'user': UserSerializer().serialize(second_most_played),
                'total': 1
            },
        ]

    def should_return_played_tracs_since_selected_date(self):
        most_played = TrackFactory()
        second_most_played = TrackFactory()
        entries = [
            PlaylistHistoryFactory(track=most_played),
            PlaylistHistoryFactory(track=most_played),
            PlaylistHistoryFactory(track=second_most_played),
            PlaylistHistoryFactory(
                track=second_most_played,
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc())
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', since='2015-06-01')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_track'] == [
            {
                'track': TrackSerializer().serialize(most_played),
                'total': 2
            },
            {
                'track': TrackSerializer().serialize(second_most_played),
                'total': 1
            },
        ]

    def should_return_played_tracs_from_the_beginning_of_the_world(self):
        most_played = TrackFactory()
        second_most_played = TrackFactory()
        entries = [
            PlaylistHistoryFactory(track=most_played),
            PlaylistHistoryFactory(track=most_played),
            PlaylistHistoryFactory(track=second_most_played),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_track'] == [
            {
                'track': TrackSerializer().serialize(most_played),
                'total': 2
            },
            {
                'track': TrackSerializer().serialize(second_most_played),
                'total': 1
            },
        ]

    def should_return_most_played_artist_since_selected_date(self):
        most_played = ArtistFactory()
        second_most_played = ArtistFactory()
        entries = [
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(artists=[most_played])
                )
            ),
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[second_most_played, most_played]
                    )
                )
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc())
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', since='2015-06-01')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_artist'] == [
            {
                'artist': ArtistSerializer().serialize(most_played),
                'total': 2
            },
            {
                'artist': ArtistSerializer().serialize(second_most_played),
                'total': 1
            },
        ]

    def should_return_most_played_artist_from_the_beginning_of_the_world(self):
        most_played = ArtistFactory()
        second_most_played = ArtistFactory()
        entries = [
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(artists=[most_played])
                )
            ),
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[second_most_played, most_played]
                    )
                )
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_artist'] == [
            {
                'artist': ArtistSerializer().serialize(most_played),
                'total': 2
            },
            {
                'artist': ArtistSerializer().serialize(second_most_played),
                'total': 1
            },
        ]
