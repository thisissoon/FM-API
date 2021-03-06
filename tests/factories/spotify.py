#!/usr/bin/env python
# encoding: utf-8

"""
tests.factories.spotify
=======================

SQLAlchemy Factories for Spotify models.
"""

# Standard Libs
from datetime import datetime

# Third Party Libs
import factory
from dateutil import tz
from factory import fuzzy
from tests.factories import UUID4, Factory
from tests.factories.user import UserFactory

# First Party Libs
from fm.models.spotify import Album, Artist, Genre, PlaylistHistory, Track


class GenreFactory(Factory):
    """ Genre Model Factory
    """

    class Meta:
        model = Genre

    id = UUID4()
    name = factory.LazyAttribute(lambda o: u'Genre {0}'.format(o.id))


class ArtistFactory(Factory):
    """ Artist Model Factory
    """

    class Meta:
        model = Artist

    id = UUID4()
    spotify_uri = factory.LazyAttribute(lambda o: 'spotify:artist:{0}'.format(o.id))
    name = factory.LazyAttribute(lambda o: u'Artist {0}'.format(o.id))


class AlbumFactory(Factory):
    """ Album Model Factory.
    """

    class Meta:
        model = Album

    id = UUID4()
    spotify_uri = factory.LazyAttribute(lambda o: 'spotify:album:{0}'.format(o.id))
    name = factory.LazyAttribute(lambda o: u'Album {0}'.format(o.id))
    images = factory.LazyAttribute(lambda o: [
        {
            "url": "https://i.scdn.co/image/4204c11e3055cd980c987ecb4658a0fe447b8156",
            "width": 640,
            "height": 640
        }, {
            "url": "https://i.scdn.co/image/b12fb1a96dbf2ffeef0dcf831935428ad8dc8d2d",
            "width": 300,
            "height": 300
        }, {
            "url": "https://i.scdn.co/image/302e4c7ad2b69c2ae52c796b835b336d0ff4cc8f",
            "width": 64,
            "height": 64
        }
    ])


class AlbumWithArtist(AlbumFactory):
    """ AlbumFactory Model which attaches an album to an Artist
    """

    artists = factory.LazyAttribute(lambda o: [ArtistFactory()])


class TrackFactory(Factory):
    """ Track Model Factory
    """

    class Meta:
        model = Track

    id = UUID4()
    spotify_uri = factory.LazyAttribute(lambda o: 'spotify:track:{0}'.format(o.id))
    name = factory.LazyAttribute(lambda o: u'Album {0}'.format(o.id))
    album = factory.SubFactory(AlbumWithArtist)
    duration = fuzzy.FuzzyInteger(1000, 10000)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        self.artists.append(ArtistFactory())


class PlaylistHistoryFactory(Factory):
    """ Factory for generating Playlist Hisotry entries
    """

    class Meta:
        model = PlaylistHistory

    id = UUID4()
    track = factory.LazyAttribute(lambda o: TrackFactory())
    user = factory.LazyAttribute(lambda o: UserFactory())
    created = factory.LazyAttribute(lambda o: datetime.now(tz.tzutc()))
