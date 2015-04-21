#!/usr/bin/env python
# encoding: utf-8

"""
tests.tasks.test_queue
======================

Unit Tests for Celery Queue Tasks
"""

import json
import mock

from fm.ext import config, db
from fm.models.spotify import Album, Artist, Track
from fm.tasks.queue import add
from fm.models.user import User
from mockredis import mock_redis_client
from tests import TRACK_DATA
from tests.factories.spotify import AlbumFactory, ArtistFactory, TrackFactory
from tests.factories.user import UserFactory


class TestAdd(object):

    def setup(self):
        user = UserFactory()

        db.session.add(user)
        db.session.commit()

        self.user = User.query.one()

        patch = mock.patch('fm.logic.player.redis', mock_redis_client())
        self.redis = patch.start()
        self.redis.publish = mock.MagicMock()
        self.addPatchCleanup(patch)

        patch = mock.patch('fm.tasks.queue.update_genres')
        self.update_genres = patch.start()
        self.update_genres.return_value = []
        self.addPatchCleanup(patch)

    def should_create_new_album(self):
        assert Album.query.count() == 0

        add.delay(TRACK_DATA, self.user.id)

        album = Album.query.one()

        assert album.name == TRACK_DATA['album']['name']
        assert album.spotify_uri == TRACK_DATA['album']['uri']

    def should_update_existing_album(self):
        album = AlbumFactory(name='Foo', spotify_uri=TRACK_DATA['album']['uri'])

        db.session.add(album)
        db.session.commit()

        assert Album.query.count() == 1

        add.delay(TRACK_DATA, self.user.id)

        album = Album.query.one()

        assert not album.name == 'Foo'
        assert album.name == TRACK_DATA['album']['name']
        assert album.spotify_uri == TRACK_DATA['album']['uri']

    def should_create_new_track(self):
        assert Track.query.count() == 0

        add.delay(TRACK_DATA, self.user.id)

        track = Track.query.one()

        assert track.name == TRACK_DATA['name']
        assert track.spotify_uri == TRACK_DATA['uri']
        assert track.album_id == Album.query.first().id

    def should_update_existing_track(self):
        album = AlbumFactory(spotify_uri=TRACK_DATA['album']['uri'])
        track = TrackFactory(name='Foo', spotify_uri=TRACK_DATA['uri'], album=album)

        db.session.add_all([album, track])
        db.session.commit()

        assert Track.query.count() == 1

        add.delay(TRACK_DATA, self.user.id)

        track = Track.query.one()

        assert not track.name == 'Foo'
        assert track.name == TRACK_DATA['name']
        assert track.spotify_uri == TRACK_DATA['uri']
        assert track.album_id == Album.query.first().id

    def should_create_new_artist(self):
        Artist.query.count() == 0

        add.delay(TRACK_DATA, self.user.id)

        artist = Artist.query.one()

        assert artist.name == TRACK_DATA['artists'][0]['name']
        assert artist.spotify_uri == TRACK_DATA['artists'][0]['uri']
        assert Album.query.first() in artist.albums

    def should_update_existing_artist(self):
        artist = ArtistFactory(name='Foo', spotify_uri=TRACK_DATA['artists'][0]['uri'])

        db.session.add(artist)
        db.session.commit()

        add.delay(TRACK_DATA, self.user.id)

        artist = Artist.query.one()

        assert not artist.name == 'Foo'
        assert artist.name == TRACK_DATA['artists'][0]['name']
        assert artist.spotify_uri == TRACK_DATA['artists'][0]['uri']
        assert Album.query.first() in artist.albums

    def should_add_track_to_playlist_and_publish_event(self):
        add.delay(TRACK_DATA, self.user.id)

        queue = self.redis.get(config.PLAYLIST_REDIS_KEY)
        user = User.query.one()

        assert len(queue) == 1
        assert json.loads(queue[0])['user'] == user.id
        assert json.loads(queue[0])['uri'] == TRACK_DATA['uri']
        assert self.redis.publish.caled_once_with(json.dumps({
            'event': 'add',
            'uri': TRACK_DATA['uri'],
            'user': user.id
        }))
