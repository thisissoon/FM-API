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
    GenreFactory,
    PlaylistHistoryFactory,
    TrackFactory,
    UserFactory
)

# First Party Libs
from fm.ext import db
from fm.serializers.spotify import ArtistSerializer, TrackSerializer
from fm.serializers.user import UserSerializer


class TestGetStats(object):

    def should_return_most_played_djs_from_selected_date(self):
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

        url = url_for('player.stats', **{'from': '2015-06-01'})
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

    def should_return_most_played_djs_in_selected_time_window(self):
        most_played = UserFactory()
        entries = [
            PlaylistHistoryFactory(
                user=most_played,
                created=datetime.datetime(2015, 5, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 7, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 3, 1, tzinfo=tzutc())
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', **{'to': '2015-06-01', 'from': '2015-04-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_active_djs'] == [
            {
                'user': UserSerializer().serialize(most_played),
                'total': 1
            },
        ]

    def should_return_most_played_djs_from_the_beginning_of_the_age(self):
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

    def should_return_played_tracs_from_selected_date(self):
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

        url = url_for('player.stats', **{'from': '2015-06-01'})
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

    def should_return_played_tracs_from_in_selected_time_windowe(self):
        most_played = TrackFactory()
        entries = [
            PlaylistHistoryFactory(
                track=most_played,
                created=datetime.datetime(2015, 5, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 7, 1, tzinfo=tzutc())
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', **{'to': '2015-06-01', 'from': '2015-04-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_tracks'] == [
            {
                'track': TrackSerializer().serialize(most_played),
                'total': 1
            }
        ]

    def should_return_played_tracs_from_the_beginning_of_the_age(self):
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
        most_played = ArtistFactory()
        second_most_played = ArtistFactory()
        entries = [
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(artists=[most_played])
                )
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc()),
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[second_most_played, most_played]
                    )
                )
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', **{'from': '2015-06-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_artists'] == [
            {
                'artist': ArtistSerializer().serialize(most_played),
                'total': 1
            },
        ]

    def should_return_most_played_artist_from_the_beginning_of_the_age(self):
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

    def should_return_most_played_artist_in_selected_time_window(self):
        most_played = ArtistFactory()
        entries = [
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 5, 1, tzinfo=tzutc()),
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[most_played]
                    )
                )
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 3, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 7, 1, tzinfo=tzutc())
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', **{'to': '2015-06-01', 'from': '2015-04-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_artists'] == [
            {
                'artist': ArtistSerializer().serialize(most_played),
                'total': 1
            },
        ]

    def should_return_most_played_genre_from_the_beginning_of_the_age(self):
        most_played = GenreFactory()
        second_most_played = GenreFactory()
        entries = [
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[ArtistFactory(
                            genres=[most_played])
                        ]
                    )
                )
            ),
            PlaylistHistoryFactory(
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[ArtistFactory(
                            genres=[second_most_played, most_played])
                        ]
                    )
                )
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats')
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
        most_played = GenreFactory()
        second_most_played = GenreFactory()
        entries = [
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
                )
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', **{'from': '2015-06-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_genres'] == [
            {
                'name': most_played.name,
                'total': 1
            },
        ]

    def should_return_most_played_genre_in_selected_window(self):
        most_played = GenreFactory()
        entries = [
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 3, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 7, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 5, 1, tzinfo=tzutc()),
                track=TrackFactory(
                    album=AlbumWithArtist(
                        artists=[ArtistFactory(
                            genres=[most_played])]
                    )
                )
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', **{'to': '2015-06-01', 'from': '2015-04-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['most_played_genres'] == [
            {
                'name': most_played.name,
                'total': 1
            },
        ]

    def should_return_user_played_time_from_the_beginning_of_the_age(self):
        most_played = UserFactory()
        second_most_played = UserFactory()
        entries = [
            PlaylistHistoryFactory(
                user=most_played,
                track=TrackFactory(duration=1000)),
            PlaylistHistoryFactory(
                user=most_played,
                track=TrackFactory(duration=500)),
            PlaylistHistoryFactory(
                user=second_most_played,
                track=TrackFactory(duration=700)),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total_play_time_per_user'] == [
            {
                'user': UserSerializer().serialize(most_played),
                'total': 1500
            },
            {
                'user': UserSerializer().serialize(second_most_played),
                'total': 700
            },
        ]

    def should_return_user_played_time_from_selected_date(self):
        most_played = UserFactory()
        second_most_played = UserFactory()
        entries = [
            PlaylistHistoryFactory(
                user=most_played,
                track=TrackFactory(duration=1000)),
            PlaylistHistoryFactory(
                user=most_played,
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc()),
                track=TrackFactory(duration=500)),
            PlaylistHistoryFactory(
                user=second_most_played,
                track=TrackFactory(duration=700)),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', **{'from': '2015-06-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total_play_time_per_user'] == [
            {
                'user': UserSerializer().serialize(most_played),
                'total': 1000
            },
            {
                'user': UserSerializer().serialize(second_most_played),
                'total': 700
            },
        ]

    def should_return_total_played_time_from_the_beginning_of_the_age(self):
        entries = [
            PlaylistHistoryFactory(
                track=TrackFactory(duration=1000)),
            PlaylistHistoryFactory(
                track=TrackFactory(duration=500)),
            PlaylistHistoryFactory(
                track=TrackFactory(duration=700)),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total_play_time'] == 2200

    def should_return_total_played_time_from_selected_date(self):
        entries = [
            PlaylistHistoryFactory(
                track=TrackFactory(duration=1000)),
            PlaylistHistoryFactory(
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc()),
                track=TrackFactory(duration=500)),
            PlaylistHistoryFactory(
                track=TrackFactory(duration=700)),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', **{'from': '2015-06-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total_play_time'] == 1700

    def should_return_total_played_time_in_selected_time_window(self):
        entries = [
            PlaylistHistoryFactory(
                track=TrackFactory(duration=1000),
                created=datetime.datetime(2015, 5, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 7, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 3, 1, tzinfo=tzutc())
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', **{'to': '2015-06-01', 'from': '2015-04-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total_play_time'] == 1000

    def should_return_total_plays_from_the_beginning_of_the_age(self):
        entries = [
            PlaylistHistoryFactory(),
            PlaylistHistoryFactory(),
            PlaylistHistoryFactory()
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total_plays'] == 3

    def should_return_total_plays_from_selected_date(self):
        entries = [
            PlaylistHistoryFactory(),
            PlaylistHistoryFactory(),
            PlaylistHistoryFactory(
                created=datetime.datetime(2014, 1, 1, tzinfo=tzutc()),
            )
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', **{'from': '2015-06-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total_plays'] == 2

    def should_return_total_plays_in_selected_time_window(self):
        entries = [
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 5, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 7, 1, tzinfo=tzutc())
            ),
            PlaylistHistoryFactory(
                created=datetime.datetime(2015, 3, 1, tzinfo=tzutc())
            ),
        ]
        db.session.add_all(entries)
        db.session.commit()

        url = url_for('player.stats', **{'to': '2015-06-01', 'from': '2015-04-01'})
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total_plays'] == 1
