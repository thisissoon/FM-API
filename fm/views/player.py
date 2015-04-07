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
from fm.models.spotify import Album, Artist, PlaylistHistory, Track
from fm.session import authenticated, current_user
from fm.models.user import User
from fm.serializers.player import PlaylistSerializer, VolumeSerializer
from fm.serializers.spotify import TrackSerializer, HistorySerializer
from fm.serializers.user import UserSerializer
from kim.exceptions import MappingErrors
from sqlalchemy import desc


class PauseView(MethodView):
    """ The pause resources allows the payer to paused and unpaused via
    POST for pause and DELTETE to unpause the player.
    """

    @authenticated
    def post(self):
        """ Pauses the player.
        """

        redis.publish(config.PLAYER_CHANNEL, json.dumps({'event': 'pause'}))

        return http.Created()

    @authenticated
    def delete(self):
        """ Unapuses the player.
        """

        redis.publish(config.PLAYER_CHANNEL, json.dumps({'event': 'resume'}))

        return http.NoContent()


class VolumeView(MethodView):
    """ Contorls Volume on the Physical player.
    """

    def get(self):
        """ Retrieve the current volume level for the physical player.
        """

        try:
            volume = int(redis.get('fm:player:volume'))
        except ValueError:
            volume = 100

        return http.OK({'volume': volume})

    @authenticated
    def post(self):
        """ Change the volume level for the player.
        """

        serializer = VolumeSerializer()

        try:
            data = serializer.marshal(request.json)
        except MappingErrors as e:
            return http.UnprocessableEntity(errors=e.message)

        redis.publish(config.PLAYER_CHANNEL, json.dumps({
            'event': 'set_volume',
            'volume': data['volume']
        }))

        return http.OK()


class MuteView(MethodView):
    """ Controls mute state of the Player.
    """

    def get(self):
        """ Returns the current mute state of the player
        """

        mute = redis.get('fm:player:mute')
        if mute is None:
            mute = 0

        try:
            value = bool(int(mute))
        except ValueError:
            value = False

        return http.OK({'mute': value})

    @authenticated
    def post(self):
        """ Set the player mute state to True.
        """

        redis.publish(config.PLAYER_CHANNEL, json.dumps({
            'event': 'set_mute',
            'mute': True
        }))

        return http.Created()

    @authenticated
    def delete(self):
        """ Set the player mute state to False.
        """

        redis.publish(config.PLAYER_CHANNEL, json.dumps({
            'event': 'set_mute',
            'mute': False
        }))

        return http.NoContent()


class CurrentView(MethodView):
    """ Operates on the currently playing track.
    """

    def get_current_track(self):
        """ Returns the currently playing track from redis.

        Returns
        -------
        fm.models.spotify.Teack
            The currently playing track or None
        """

        current = redis.get('fm:player:current')
        if current is None:
            return None, None

        uri, user = json.loads(current).values()

        track = Track.query.filter(Track.spotify_uri == uri).first()
        user = User.query.filter(User.id == user).first()

        return track, user

    def get(self):
        """ Returns the currently playing track.

        Returns
        -------
        http.Response
            A http response instance, 204 or 200
        """

        track, user = self.get_current_track()
        if track is None or user is None:
            return http.NoContent()

        try:
            paused = int(redis.get('fm:player:paused'))
        except (ValueError, TypeError):
            paused = 0

        headers = {
            'Paused': paused
        }

        response = {
            'track': TrackSerializer().serialize(track),
            'user': UserSerializer().serialize(user),
        }

        return http.OK(response, headers=headers)

    @authenticated
    def delete(self):
        """ Skips the currently playing track.

        Returns
        -------
        http.Response
            A http response intance, in this case it should always be a 204
        """

        track = self.get_current_track()
        if track is None:
            return http.NoContent()

        redis.publish(
            config.PLAYER_CHANNEL,
            json.dumps({
                'event': 'stop'
            })
        )

        return http.NoContent()


class HisotryView(MethodView):
    """ Playlist History Resource for tracking the hisotry of played tracks.
    """

    @http.pagination.paginate()
    def get(self, *args, **kwargs):
        """ Returns a paginated play list history.
        """

        total = PlaylistHistory.query.count()

        rows = db.session.query(PlaylistHistory) \
            .order_by(desc(PlaylistHistory.created)) \
            .limit(kwargs.get('limit')) \
            .offset(kwargs.get('offset')) \
            .all()

        return http.OK(
            HistorySerializer().serialize(rows, many=True),
            limit=kwargs.get('limit'),
            page=kwargs.get('page'),
            total=total)


class QueueView(MethodView):
    """ The Track resource allows for the management of the playlist.
    """

    @http.pagination.paginate()
    def get(self, *args, **kwargs):
        """ Returns a paginated list of tracks currently in the playlist.
        """

        offset = kwargs.pop('offset')
        limit = kwargs.pop('limit')

        queue = redis.lrange(config.PLAYLIST_REDIS_KEY, offset, (offset + limit - 1))
        total = redis.llen(config.PLAYLIST_REDIS_KEY)

        response = []

        if total > 0:
            for item in queue:
                item = json.loads(item)
                track = Track.query.filter(Track.spotify_uri == item['uri']).first()
                user = User.query.filter(User.id == item['user']).first()
                if track is not None and user is not None:
                    response.append({
                        'track': TrackSerializer().serialize(track),
                        'user': UserSerializer().serialize(user)
                    })

        return http.OK(
            response,
            page=kwargs.get('page'),
            total=total,
            limit=limit)

    # TODO: Refactor this resource, its getting a tad large
    @authenticated
    def post(self):
        """ Allows you to add anew track to the player playlist.
        """

        serializer = PlaylistSerializer()
        try:
            track = serializer.marshal(request.json)
        except MappingErrors as e:
            return http.UnprocessableEntity(errors=e.message)

        album = Album.query.filter(Album.spotify_uri == track['track']['album']['uri']).first()
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

        # If a track is skipped we should decrement the play count
        try:
            track.play_count += 1
        except TypeError as e:
            track.play_count = 1

        db.session.commit()

        # Add track to the Queue - Also storing the current user ID
        redis.rpush(config.PLAYLIST_REDIS_KEY, json.dumps({
            'uri': track.spotify_uri,
            'user': current_user.id}))

        # Publish the Add event
        redis.publish(config.PLAYER_CHANNEL, json.dumps({
            'event': 'add',
            'uri': track.spotify_uri,
            'user': current_user.id
        }))

        return http.Created(location=url_for('tracks.track', pk_or_uri=track.id))
