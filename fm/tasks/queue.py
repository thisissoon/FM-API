#!/usr/bin/env python
# encoding: utf-8

"""
fm.tasks.queue
==============

Celery Tasks for the Player Queue.
"""

# First Party Libs
from fm.ext import celery, db
from fm.logic.player import Queue
from fm.models.spotify import Album, Artist, Track
from fm.thirdparty.spotify import SpotifyApi


@celery.task
def add_album(uri, user):
    '''
    Celery task for adding album tracks into the queue

    Arguments
    ---------
    data : uri
        URI of album to add

    user : str
        Id of the user whom aded t otrack to the queue
    '''
    spotify_api = SpotifyApi()
    add_arguments = []
    for i, track in enumerate(spotify_api.get_album_tracks(uri)):
        add_arguments.append((track.raw, user, i < 1))
    add.starmap(add_arguments).apply_async()


@celery.task
def add(data, user, notification=True):
    """ Celery task for adding a single track to the queue.

    Arguments
    ---------
    data : dict
        Raw Decoded Spotify API Track JSON data
    user : str
        Id of the user whom added the track to the queue
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
    album_id = album.id  # keep album id outside of session

    # Crate or Update Track

    track = Track.query.filter(Track.spotify_uri == data['uri']).first()
    if track is None:
        track = Track()

    track.name = data['name']
    track.spotify_uri = data['uri']
    track.duration = data['duration_ms']
    track.album_id = album_id

    db.session.add(track)
    db.session.commit()
    Queue.add(track.spotify_uri, user, notification)

    # Create or Update Artists - Appending Album to the Artists Albums
    for item in data['artists']:
        artist = Artist.query.filter(Artist.spotify_uri == item['uri']).first()
        if artist is None:
            artist = Artist()

        artist.name = item['name']
        artist.spotify_uri = item['uri']

        if album_id not in [x.id for x in artist.albums]:
            artist.albums.append(album)

        if track.id not in [x.id for x in artist.tracks]:
            artist.tracks.append(track)

        db.session.add(artist)
        db.session.commit()
