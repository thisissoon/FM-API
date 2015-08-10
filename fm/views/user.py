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

# First Party Libs
from fm import http
from fm.logic import stats
from fm.logic.oauth import update_spotify_credentials
from fm.models.spotify import PlaylistHistory
from fm.models.user import User
from fm.serializers.spotify import ArtistSerializer
from fm.serializers.user import UserSerializer
from fm.session import authenticated, current_user
from fm.thirdparty.spotify import (
    PlaylistSerializer,
    SpotifyApi,
    TrackSerializer
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

    def total_play_time(self, user_pk, since, until):
        query = stats.total_play_time(since).filter(
            PlaylistHistory.user_id == user_pk
        )
        return query.first()[0]

    def total_plays(self, user_pk, since, until):
        query = stats.total_plays(since).filter(
            PlaylistHistory.user_id == user_pk
        )
        return query.count()

    def most_played_tracks(self, user_pk, since, until):
        query = stats.most_played_tracks(since).filter(
            PlaylistHistory.user_id == user_pk
        )
        return query.limit(10)

    def most_played_artists(self, user_pk, since, until):
        query = stats.most_played_artists(since).filter(
            PlaylistHistory.user_id == user_pk
        )
        return query.limit(10)

    def most_played_genres(self, user_pk, since, until):
        query = stats.most_played_genres(since).filter(
            PlaylistHistory.user_id == user_pk
        )
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

        since = request.args.get('from', None)
        if since:
            since = pytz.utc.localize(datetime.strptime(since, '%Y-%m-%d'))
        until = request.args.get('to', None)
        if until:
            until = pytz.utc.localize(datetime.strptime(until, '%Y-%m-%d'))

        payload = {
            'most_played_tracks': [
                {
                    'track': TrackSerializer().serialize(u),
                    'total': t
                } for u, t in self.most_played_tracks(pk, since, until)],
            'most_played_artists': [
                {
                    'artist': ArtistSerializer().serialize(u),
                    'total': t
                } for u, t in self.most_played_artists(pk, since, until)],
            'most_played_genres': [
                {
                    'name': u.name,
                    'total': t
                } for u, t in self.most_played_genres(pk, since, until)],
            'total_plays': self.total_plays(pk, since, until),
            'total_play_time': self.total_play_time(pk, since, until),
        }
        return http.OK(payload)
