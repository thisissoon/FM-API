#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.player
===============

Views for handling /player API resource requests.
"""

import json

from flask import request, url_for
from flask.views import MethodView
from fm import http
from fm.ext import config, db, redis
from fm.models.spotify import Album, Artist, Track
from fm.serializers.player import PlaylistSerializer
from fm.serializers.spotify import TrackSerialzier
from kim.exceptions import MappingErrors
from sqlalchemy.dialects.postgresql import Any, array


class Pause(MethodView):
    """ The pause resources allows the payer to paused and unpaused via
    POST for pause and DELTETE to unpause the player.
    """

    def post(self):
        """ Pauses the player.
        """

        redis.publish(config.PLAYER_CHANNEL, json.dumps({'event': 'pause'}))

        return http.Created()

    def delete(self):
        """ Unapuses the player.
        """

        redis.publish(config.PLAYER_CHANNEL, json.dumps({'event': 'resume'}))

        return http.NoContent()


class Playlist(MethodView):
    """ The Track resource allows for the management of the playlist.
    """

    @http.pagination.paginate()
    def get(self, *args, **kwargs):
        """ Returns a paginated list of tracks currently in the playlist.
        """

        offset = kwargs.pop('offset')
        limit = kwargs.pop('limit')

        tracks = redis.lrange('playlist', offset, (offset + limit - 1))
        total = redis.llen('playlist')

        rows = Track.query \
            .filter(Any(Track.spotify_uri, array(tracks))) \
            .all()

        return http.OK(
            TrackSerialzier().serialize(rows, many=True),
            page=kwargs.get('page'),
            total=total,
            limit=limit)

    def post(self):
        """ Allows you to add anew track to the player playlist.
        """

        serializer = PlaylistSerializer()
        try:
            serializer.marshal(request.json)
        except MappingErrors as e:
            return http.UnprocessableEntity(errors=e.message)

        data = serializer.track

        album = Album.query.filter(Album.spotify_uri == data['album']['uri']).first()
        if album is None:
            album = Album()
            db.session.add(album)

        album.name = data['album']['name']
        album.images = data['album']['images']
        album.spotify_uri = data['album']['uri']

        db.session.commit()

        for item in data['artists']:
            artist = Artist.query.filter(Artist.spotify_uri == item['uri']).first()
            if artist is None:
                artist = Artist()
                db.session.add(artist)

            artist.name = item['name']
            artist.spotify_uri = item['uri']

            if artist not in album.artists:
                album.artists.append(artist)

            db.session.commit()

        track = Track.query.filter(Track.spotify_uri == data['uri']).first()
        if track is None:
            track = Track()
            db.session.add(track)

        track.name = data['name']
        track.spotify_uri = data['uri']
        track.duration = data['duration_ms']
        track.album_id = album.id

        db.session.commit()

        redis.rpush('playlist', track.spotify_uri)

        return http.Created(location=url_for('tracks.track', pk=track.id))
