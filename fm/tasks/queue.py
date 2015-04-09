#!/usr/bin/env python
# encoding: utf-8

"""
fm.tasks.queue
==============

Celery Tasks for the Player Queue.
"""

from fm.ext import celery, db
from fm.models.spotify import Album, Artist, Track
from fm.logic.player import Queue


@celery.task
def add(data, user):
    """ Celery task for adding a single track to the queue.

    Arguments
    ---------
    data : dict
        Raw Decoded Spotify API Track JSON data
    user : str
        The name of the user whom added the track to the queue
    """

    # Create or Update Album

    album = Album.query.filter(Album.spotify_uri == data['album']['uri']).first()
    if album is None:
        album = Album()

    album.name = data['album']['name']
    album.images = data['album']['images']
    album.spotify_uri = data['album']['uri']

    db.session.add(album)
    db.session.commit()

    # Crate or Update Track

    track = Track.query.filter(Track.spotify_uri == data['uri']).first()
    if track is None:
        track = Track()

    track.name = data['name']
    track.spotify_uri = data['uri']
    track.duration = data['duration_ms']
    track.album_id = album.id

    db.session.add(track)
    db.session.commit()

    # Create or Update Artists - Appending Album to the Artists Albums

    for item in data['artists']:
        artist = Artist.query.filter(Artist.spotify_uri == item['uri']).first()
        if artist is None:
            artist = Artist()

        artist.name = item['name']
        artist.spotify_uri = item['uri']

        if album not in artist.albums:
            artist.albums.append(album)

        db.session.add(artist)
        db.session.commit()

    # Append Track to Queue

    Queue.add(track, user)
