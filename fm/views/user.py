#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.user
=============

Views for working with User objects.
"""

# Standard Libs
import uuid
from datetime import datetime

# Third Party Libs
import pytz
from flask import request
from flask.views import MethodView
from sqlalchemy import desc
from sqlalchemy.orm import lazyload
from sqlalchemy.sql import func

# First Party Libs
from fm import http
from fm.logic.oauth import update_spotify_credentials
from fm.models.user import User
from fm.serializers.user import UserSerializer
from fm.session import authenticated, current_user
from fm.thirdparty.spotify import (
    PlaylistSerializer,
    SpotifyApi,
    TrackSerializer
)
from fm.models.spotify import (
    Album,
    Artist,
    ArtistAlbumAssociation,
    ArtistGenreAssociation,
    Genre,
    PlaylistHistory,
    Track
)
from fm.serializers.spotify import (
    ArtistSerializer
)


class UserAuthenticatedView(MethodView):
    """ Authenticated User Resource - returns the currently authenticated user.
    """

    @authenticated
    def get(self):
        """ Returns the currently authenticated user
        """

        return http.OK(UserSerializer().serialize(current_user))


class UserView(MethodView):
    """ View for getting user object
    """

    def get(self, pk):
        """ Get a serialized user object.

        Arguments
        ---------
        pk : str
            The user primary key UUID
        """

        try:
            uuid.UUID(pk, version=4)
        except ValueError:
            user = None
        else:
            user = User.query.get(pk)

        if user is None:
            return http.NotFound()

        return http.OK(UserSerializer().serialize(user))


class UserSpotifyPlaylistView(MethodView):

    def get(self, user_pk):
        """ Get user's playlists.
        If user is not authorized its Spotify account view returns HTTP code
        for NO CONTENT
        Arguments
        ---------
        user_pk: str
            The user primary key UUID
        """
        user = User.query.get(user_pk)
        if user.spotify_id is None:
            return http.NoContent('User hasn\'t authorized Spotify account')
        update_spotify_credentials(user)

        spotify_api = SpotifyApi(user)
        return http.OK(PlaylistSerializer().serialize(
            [pl for pl in spotify_api.playlist_iterator()],
            many=True
        ))


class UserSpotifyTracksView(MethodView):

    def get(self, user_pk, playlist_pk):
        """ Get user's track in particular playlist.
        If user is not authorized its Spotify account view returns HTTP code
        for NO CONTENT
        Arguments
        ---------
        user_pk: str
            The user primary key UUID
        playlist_pk: str
            The playlist spotify id
        """
        user = User.query.get(user_pk)
        if user.spotify_id is None:
            return http.NoContent('User hasn\'t authorized Spotify account')
        update_spotify_credentials(user)

        spotify_api = SpotifyApi(user)
        return http.OK(TrackSerializer().serialize(
            [pl for pl in spotify_api.get_playlists_tracks(playlist_pk)],
            many=True
        ))


class UserStatsView(MethodView):
    """ Provides statistics for a specific user.
    """

    def total_play_time(self, user_pk, since):
        query = Track.query \
            .with_entities(func.sum(Track.duration).label('sum')) \
            .join(PlaylistHistory) \
            .filter(PlaylistHistory.user_id == user_pk)

        if since:
            query = query.filter(PlaylistHistory.created >= since)
        return query.first()[0]

    def total_plays(self, user_pk, since):
        query = PlaylistHistory.query \
            .filter(PlaylistHistory.user_id == user_pk)
        if since:
            query = query.filter(PlaylistHistory.created >= since)
        return query.count()

    def most_played_tracks(self, user_pk, since):
        query = Track.query \
            .options(lazyload(Track.album)) \
            .with_entities(Track, func.count(Track.id).label('count')) \
            .join(PlaylistHistory) \
            .filter(PlaylistHistory.user_id == user_pk) \
            .group_by(Track.id) \
            .order_by(desc('count'))
        if since:
            query = query.filter(PlaylistHistory.created >= since)
        return query.limit(10)

    def most_played_artists(self, user_pk, since):
        query = Artist.query \
            .with_entities(Artist, func.count(Artist.id).label('count')) \
            .join(ArtistAlbumAssociation) \
            .join(Album) \
            .join(Track) \
            .join(PlaylistHistory) \
            .filter(PlaylistHistory.user_id == user_pk) \
            .group_by(Artist.id) \
            .order_by(desc('count'))
        if since:
            query = query.filter(PlaylistHistory.created >= since)
        return query.limit(10)

    def most_played_genres(self, user_pk, since):
        query = Genre.query \
            .with_entities(Genre, func.count(Genre.id).label('count')) \
            .join(ArtistGenreAssociation) \
            .join(Artist) \
            .join(ArtistAlbumAssociation) \
            .join(Album) \
            .join(Track) \
            .join(PlaylistHistory) \
            .filter(PlaylistHistory.user_id == user_pk) \
            .group_by(Genre.id) \
            .order_by(desc('count'))
        if since:
            query = query.filter(PlaylistHistory.created >= since)
        return query.limit(10)

    def get(self, pk):

        try:
            uuid.UUID(pk, version=4)
        except ValueError:
            user = None
        else:
            user = User.query.get(pk)

        if user is None:
            return http.NotFound()

        since = request.args.get('since', None)
        if since:
            since = pytz.utc.localize(datetime.strptime(since, '%Y-%m-%d'))

        stats = {
            'most_played_tracks': [
                {
                    'track': TrackSerializer().serialize(u),
                    'total': t
                } for u, t in self.most_played_tracks(pk, since)],
            'most_played_artists': [
                {
                    'artist': ArtistSerializer().serialize(u),
                    'total': t
                } for u, t in self.most_played_artists(pk, since)],
            'most_played_genres': [
                {
                    'name': u.name,
                    'total': t
                } for u, t in self.most_played_genres(pk, since)],
            'total_plays': self.total_plays(pk, since),
            'total_play_time': self.total_play_time(pk, since),
        }
        return http.OK(stats)
