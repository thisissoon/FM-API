#!/usr/bin/env python
# encoding: utf-8

"""
tests.tasks.test_artist
=======================

Unittests for Artist Celery Tasks.
"""

# Standard Libs
import uuid

# Third Party Libs
import mock
from tests.factories.spotify import ArtistFactory

# First Party Libs
from fm.ext import db
from fm.models.spotify import Artist, Genre
from fm.tasks.artist import update_genres
from fm.thirdparty.echonest import EchoNestError


class TestUpdateGenres(object):

    def setup(self):
        patch = mock.patch('fm.tasks.artist.get_artist_genres')
        self.get_artist_genres = patch.start()
        self.get_artist_genres.return_value = []
        self.addPatchCleanup(patch)

    def should_return_false_artist_not_found(self):
        result = update_genres.delay(unicode(uuid.uuid4()))

        assert result.wait() is False

    def should_update_artist_genres(self):
        self.get_artist_genres.side_effect = EchoNestError

        a = ArtistFactory()

        db.session.add(a)
        db.session.commit()

        result = update_genres.delay(a.id)

        assert result.wait() is False
        self.get_artist_genres.assert_called_once_with(a.spotify_uri)

    def should_udpate_artist_genres(self):
        self.get_artist_genres.return_value = ['foo', 'bar']

        a = ArtistFactory()

        db.session.add(a)
        db.session.commit()

        result = update_genres.delay(a.id)
        artist = Artist.query.all()[0]

        assert result.wait() is True
        assert Genre.query.filter(Genre.name == 'foo').first() in artist.genres
        assert Genre.query.filter(Genre.name == 'bar').first() in artist.genres
        self.get_artist_genres.assert_called_once_with(artist.spotify_uri)
