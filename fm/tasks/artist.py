#!/usr/bin/env python
# encoding: utf-8

"""
fm.tasks.artist
=================

Asynchronous tasks specifically relating to Artists.
"""

# First Party Libs
from fm.echonest import EchoNestError, get_artist_genres
from fm.ext import celery, db
from fm.models.spotify import Artist, Genre


@celery.task
def update_genres(pk):
    """ Task for updating an existing artists genres asynchronously from
    Echo Nest.

    pk : str
        The UUID Primary Key of the Artist
    """

    artist = Artist.query.get(pk)
    if artist is None:
        # TODO: Log This
        return False

    # Call Echo Nest
    try:
        genres = get_artist_genres(artist.spotify_uri)
    except EchoNestError:
        # TODO: Log This
        return False

    for name in genres:
        genre = Genre.query.filter(Genre.name == name).first()
        if genre is None:
            genre = Genre(name=name)

        if artist not in genre.artists:
            genre.artists.append(artist)

        db.session.add(genre)
        db.session.commit()

    return True
