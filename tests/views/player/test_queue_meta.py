#!/usr/bin/env python
# encoding: utf-8

"""
tests.views.player.test_queue_meta
=============================

Unit tests for the ``fm.views.player.QueueMetaView`` class.
"""

# Standard Libs
import json

# Third Pary Libs
import mock
from flask import url_for
from mockredis import mock_redis_client
from tests.factories.spotify import (
    AlbumWithArtist,
    ArtistFactory,
    GenreFactory,
    TrackFactory,
    UserFactory
)

# First Party Libs
from fm.ext import config, db


class TestQueueMeta(object):

    def setup(self):
        # Standard redis mock client to be used across multiple patches
        self.redis = mock_redis_client()
        self.redis.publish = mock.MagicMock()

        # Patch redis in the player logic module
        patch = mock.patch(
            'fm.logic.player.redis',
            new_callable=mock.PropertyMock(return_value=self.redis))
        patch.start()
        self.addPatchCleanup(patch)

        # Patch redis in the player views module
        patch = mock.patch(
            'fm.views.player.redis',
            new_callable=mock.PropertyMock(return_value=self.redis))
        patch.start()
        self.addPatchCleanup(patch)

    def should_return_non_false_values_when_something_is_in_queue(self):
        tracks = TrackFactory.create_batch(
            3,
            album=AlbumWithArtist(
                artists=[ArtistFactory(
                    genres=GenreFactory.create_batch(2)
                )]
            )
        )
        db.session.add_all(tracks)
        db.session.commit()

        for track in tracks:
            self.redis.rpush(
                config.PLAYLIST_REDIS_KEY,
                json.dumps({
                    'uri': track.spotify_uri,
                    'user': 'user'
                })
            )
        url = url_for('player.queue-meta')
        response = self.client.get(url)
        assert response.json['total']
        assert response.json['genres']
        assert response.json['users']
        assert response.json['play_time']

    def should_return_total_played_time_of_all_tracks_in_queue(self):
        tracks = TrackFactory.create_batch(3) * 2  # add some duplicates
        db.session.add_all(tracks + TrackFactory.create_batch(2))
        db.session.commit()

        for track in tracks:
            self.redis.rpush(
                config.PLAYLIST_REDIS_KEY,
                json.dumps({
                    'uri': track.spotify_uri,
                    'user': 'user'
                })
            )

        url = url_for('player.queue-meta')
        response = self.client.get(url)

        assert response.status_code == 200
        assert sum(t.duration for t in tracks) == response.json['play_time']

    def should_returns_total_number_of_trucks_in_queue(self):
        tracks = TrackFactory.create_batch(3)
        db.session.add_all(tracks)
        db.session.commit()

        for track in tracks:
            self.redis.rpush(
                config.PLAYLIST_REDIS_KEY,
                json.dumps({
                    'uri': track.spotify_uri,
                    'user': 'user'
                })
            )

        url = url_for('player.queue-meta')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['total'] == 3

    def should_returns_list_of_users_total_number_of_tracks_in_queue(self):
        tracks = TrackFactory.create_batch(3)
        users = UserFactory.create_batch(2)
        db.session.add_all(tracks + users)
        db.session.commit()

        users_in_queue = [users[0], users[0], users[1]]
        for track in tracks:
            self.redis.rpush(
                config.PLAYLIST_REDIS_KEY,
                json.dumps({
                    'uri': track.spotify_uri,
                    'user': users_in_queue.pop().id
                })
            )

        url = url_for('player.queue-meta')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['users'] == {users[0].id: 2, users[1].id: 1}

    def should_returns_list_of_genres_in_queue(self):
        genres = GenreFactory.create_batch(2)
        track1 = TrackFactory(
            album=AlbumWithArtist(
                artists=[ArtistFactory(
                    genres=genres)
                ]
            )
        )
        track2 = TrackFactory(
            album=AlbumWithArtist(
                artists=[ArtistFactory(
                    genres=[genres[0]])
                ]
            )
        )
        tracks = [track1, track2]
        db.session.add_all(tracks)
        db.session.commit()

        for track in tracks:
            self.redis.rpush(
                config.PLAYLIST_REDIS_KEY,
                json.dumps({
                    'uri': track.spotify_uri,
                    'user': 'user'
                })
            )

        url = url_for('player.queue-meta')
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.json['genres'] == {genres[0].name: 2, genres[1].name: 1}
