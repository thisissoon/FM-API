#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.player
===============

Views for handling /player API resource requests.
"""

# Standard Libs
import json
from datetime import datetime

# Third Party Libs
import pytz
from flask import request, url_for
from flask.views import MethodView
from kim.exceptions import MappingErrors
from sqlalchemy import desc
from sqlalchemy.orm import lazyload
from sqlalchemy.sql import func

# First Party Libs
from fm import http
from fm.ext import config, db, redis
from fm.logic.player import Queue, Random
from fm.models.spotify import (
    Album,
    Artist,
    ArtistAlbumAssociation,
    ArtistGenreAssociation,
    Genre,
    PlaylistHistory,
    Track
)
from fm.models.user import User
from fm.serializers.player import PlaylistSerializer, VolumeSerializer
from fm.serializers.spotify import (
    ArtistSerializer,
    HistorySerializer,
    TrackSerializer
)
from fm.serializers.user import UserSerializer
from fm.session import authenticated, current_user
from fm.tasks.queue import add


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
            'player': {
                'elapsed_time': int(redis.get('fm:player:elapsed_time')) * 1000  # ms
            }
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


class HistoryView(MethodView):
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


class StatsView(MethodView):

    def most_active_djs(self, since):
        query = User.query \
            .with_entities(User, func.count(User.id).label('count')) \
            .join(PlaylistHistory) \
            .group_by(User.id) \
            .order_by(desc('count'))
        if since:
            query = query.filter(PlaylistHistory.created >= since)
        return query.limit(10)

    def total_play_time_per_user(self, since):
        query = User.query \
            .with_entities(User, func.sum(Track.duration).label('sum')) \
            .join(PlaylistHistory) \
            .join(Track) \
            .group_by(User.id) \
            .order_by(desc('sum'))
        if since:
            query = query.filter(PlaylistHistory.created >= since)
        return query.limit(10)

    def total_play_time(self, since):
        query = Track.query.with_entities(
            func.sum(Track.duration).label('sum')
        ).join(PlaylistHistory)
        if since:
            query = query.filter(PlaylistHistory.created >= since)
        return query.first()[0]

    def most_played_track(self, since):
        query = Track.query \
            .options(lazyload(Track.album)) \
            .with_entities(Track, func.count(Track.id).label('count')) \
            .join(PlaylistHistory) \
            .group_by(Track.id) \
            .order_by(desc('count'))
        if since:
            query = query.filter(PlaylistHistory.created >= since)
        return query.limit(10)

    def most_played_artist(self, since):
        query = Artist.query \
            .with_entities(Artist, func.count(Artist.id).label('count')) \
            .join(ArtistAlbumAssociation) \
            .join(Album) \
            .join(Track) \
            .join(PlaylistHistory) \
            .group_by(Artist.id) \
            .order_by(desc('count'))
        if since:
            query = query.filter(PlaylistHistory.created >= since)
        return query.limit(10)

    def most_played_genre(self, since):
        query = Genre.query \
            .with_entities(Genre, func.count(Genre.id).label('count')) \
            .join(ArtistGenreAssociation) \
            .join(Artist) \
            .join(ArtistAlbumAssociation) \
            .join(Album) \
            .join(Track) \
            .join(PlaylistHistory) \
            .group_by(Genre.id) \
            .order_by(desc('count'))
        if since:
            query = query.filter(PlaylistHistory.created >= since)
        return query.limit(10)

    def get(self, *args, **kwargs):
        since = request.args.get('since', None)
        if since:
            since = pytz.utc.localize(datetime.strptime(since, '%Y-%m-%d'))

        stats = {
            'most_active_djs': [
                {
                    'user': UserSerializer().serialize(u),
                    'total': t
                } for u, t in self.most_active_djs(since)],
            'most_played_track': [
                {
                    'track': TrackSerializer().serialize(u),
                    'total': t
                } for u, t in self.most_played_track(since)],
            'most_played_artist': [
                {
                    'artist': ArtistSerializer().serialize(u),
                    'total': t
                } for u, t in self.most_played_artist(since)],
            'most_played_genre': [
                {
                    'name': u.name,
                    'total': t
                } for u, t in self.most_played_genre(since)],
            'total_play_time_per_user': [
                {
                    'user': UserSerializer().serialize(u),
                    'total': t
                } for u, t in self.total_play_time_per_user(since)],
            'total_play_time': self.total_play_time(since),
        }
        return http.OK(stats)


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

    @authenticated
    def post(self):
        """ Allows you to add anew track to the player playlist.
        """

        serializer = PlaylistSerializer()

        try:
            track = serializer.marshal(request.json)
        except MappingErrors as e:
            return http.UnprocessableEntity(errors=e.message)

        # Dispatch Celery Task
        add.delay(track['uri'], current_user.id)

        return http.Created(location=url_for(
            'tracks.track',
            pk_or_uri=track['uri']['uri']))


class RandomView(MethodView):

    @authenticated
    def post(self):
        response = []
        for track in Random.get_tracks(request.json['tracks']):
            response.append({
                'track': TrackSerializer().serialize(track),
                'user': UserSerializer().serialize(current_user)
            })
            Queue.add(track.spotify_uri, current_user.id)

        return http.Created(response)
