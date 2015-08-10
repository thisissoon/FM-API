#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.user.test_stats
===============================

Unit tests for the ``fm.views.user.UserStatsView`` class.
"""
# Standard Libs
import datetime

# Third Party Libs
from dateutil.tz import tzutc
from flask import url_for
from tests.factories.spotify import (
    AlbumWithArtist,
    ArtistFactory,
    GenreFactory,
    PlaylistHistoryFactory,
    TrackFactory,
    UserFactory
)

# First Party Libs
from fm.ext import db
from fm.serializers.spotify import ArtistSerializer
from fm.thirdparty.spotify import TrackSerializer


class TestGetStats(object):

    def should_return_played_tracks_from_selected_date(self):
        user = UserFactory()
        most_played = TrackFactory()
        second_most_played = TrackFactory()
        entries = [
            user,
            PlaylistHistoryFactory(track=most_played, user=user),
            PlaylistHistoryFactory(track=most_played, user=user),
            PlaylistHistoryFactory(track=second_most_played, user=user),
            PlaylistHistoryFactory(track=second_most_played),
            PlaylistHistoryFactory(
                track=second_most_played,
                user=user,
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc())
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('users.stats', pk=user.id, **{'from': '2015-06-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_tracks'] == [
            {
                'track': TrackSerializer().serialize(most_played),
                'total': 2
            },
            {
                'track': TrackSerializer().serialize(second_most_played),
                'total': 1
            },
        ]

    def should_return_played_tracks_from_the_beginning_of_the_age(self):
        user = UserFactory()
        most_played = TrackFactory()
        second_most_played = TrackFactory()
        entries = [
            user,
            PlaylistHistoryFactory(track=most_played, user=user),
            PlaylistHistoryFactory(track=most_played, user=user),
            PlaylistHistoryFactory(track=second_most_played, user=user),
            PlaylistHistoryFactory(track=second_most_played),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('users.stats', pk=user.id)
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_tracks'] == [
            {
                'track': TrackSerializer().serialize(most_played),
                'total': 2
            },
            {
                'track': TrackSerializer().serialize(second_most_played),
                'total': 1
            },
        ]

    def should_return_most_played_artist_from_selected_date(self):
        user = UserFactory()
        most_played = ArtistFactory()
        second_most_played = ArtistFactory()
        entries = [
            user,
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(artists=[most_played])
                ),
                user=user
            ),
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(artists=[second_most_played])
                )
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc()),
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[second_most_played, most_played]
                    )
                ),
                user=user
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('users.stats', pk=user.id, **{'from': '2015-06-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_artists'] == [
            {
                'artist': ArtistSerializer().serialize(most_played),
                'total': 1
            },
        ]

    def should_return_most_played_artist_from_the_beginning_of_the_age(self):
        user = UserFactory()
        most_played = ArtistFactory()
        second_most_played = ArtistFactory()
        entries = [
            user,
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(artists=[most_played])
                ),
                user=user
            ),
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[second_most_played, most_played]
                    )
                ),
                user=user
            ),
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(artists=[second_most_played])
                )
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('users.stats', pk=user.id)
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_artists'] == [
            {
                'artist': ArtistSerializer().serialize(most_played),
                'total': 2
            },
            {
                'artist': ArtistSerializer().serialize(second_most_played),
                'total': 1
            },
        ]

    def should_return_most_played_genre_from_the_beginning_of_the_age(self):
        user = UserFactory()
        most_played = GenreFactory()
        second_most_played = GenreFactory()
        entries = [
            user,
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[ArtistFactory(
                            genres=[most_played])
                        ]
                    )
                ),
                user=user
            ),
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[ArtistFactory(
                            genres=[second_most_played, most_played])
                        ]
                    )
                ),
                user=user
            ),
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[ArtistFactory(
                            genres=[second_most_played])
                        ]
                    )
                )
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('users.stats', pk=user.id)
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_genres'] == [
            {
                'name': most_played.name,
                'total': 2
            },
            {
                'name': second_most_played.name,
                'total': 1
            },
        ]

    def should_return_most_played_genre_from_selected_date(self):
        user = UserFactory()
        most_played = GenreFactory()
        second_most_played = GenreFactory()
        entries = [
            user,
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[ArtistFactory(
                            genres=[most_played])]
                    )
                ),
                user=user
            ),
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[ArtistFactory(
                            genres=[most_played])]
                    )
                )
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc()),
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[ArtistFactory(
                            genres=[second_most_played, most_played])]
                    )
                ),
                user=user
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('users.stats', pk=user.id, **{'from': '2015-06-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_genres'] == [
            {
                'name': most_played.name,
                'total': 1
            },
        ]

    def should_return_played_time_from_the_beginning_of_the_age(self):
        user = UserFactory()
        entries = [
            user,
            PlaylistHistoryFactory(
                user=user,
                track=TrackFactory(duration=1000)),
            PlaylistHistoryFactory(
                user=user,
                track=TrackFactory(duration=500)),
            PlaylistHistoryFactory(
                user=user,
                track=TrackFactory(duration=700)),
            PlaylistHistoryFactory(
                track=TrackFactory(duration=700)),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('users.stats', pk=user.id)
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total_play_time'] == 2200

    def should_return_played_time_from_selected_date(self):
        user = UserFactory()
        entries = [
            user,
            PlaylistHistoryFactory(
                user=user,
                track=TrackFactory(duration=1000)),
            PlaylistHistoryFactory(
                user=user,
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc()),
                track=TrackFactory(duration=500)),
            PlaylistHistoryFactory(
                user=user,
                track=TrackFactory(duration=700)),
            PlaylistHistoryFactory(
                track=TrackFactory(duration=700)),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('users.stats', pk=user.id, **{'from': '2015-06-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total_play_time'] == 1700

    def should_return_total_plays_from_the_beginning_of_the_age(self):
        user = UserFactory()
        entries = [
            user,
            PlaylistHistoryFactory(user=user),
            PlaylistHistoryFactory(user=user),
            PlaylistHistoryFactory()
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('users.stats', pk=user.id)
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total_plays'] == 2

    def should_return_total_plays_from_selected_date(self):
        user = UserFactory()
        entries = [
            user,
            PlaylistHistoryFactory(user=user),
            PlaylistHistoryFactory(user=user),
            PlaylistHistoryFactory(),
            PlaylistHistoryFactory(
                user=user,
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc()),
            )
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('users.stats', pk=user.id, **{'from': '2015-06-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total_plays'] == 2
