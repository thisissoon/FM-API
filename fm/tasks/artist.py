#!/usr/bin/env python
# encoding: utf-8

"""
fm.tasks.artist
=================

Asynchronous tasks specifically relating to Artists.
"""

from fm.echonest import get_artist_genres
from fm.ext import celery, db
from fm.models.spotify import Artist, Genre


@celery.task
def update_genres(uri):
    """ Task for updating an existing artists genres asynchronously from
    Echo Nest.

    uri : str
        Existing artist Spotify URI
    """

    artist = Artist.query.filter(Artist.spotify_uri == uri).first()
    if artist is None:
        return False

    # Call Echo Nest
    genres = get_artist_genres(uri)

    for name in genres:
        genre = Genre.query.filter(Genre.name == name).first()
        if genre is None:
            genre = Genre(name=name)

        if artist not in genre.artists:
            genre.artists.append(artist)

        db.session.add(genre)
        db.session.commit()

    return True
