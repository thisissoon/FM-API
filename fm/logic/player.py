"""
fm.logic.player
===========
Classes for handling and wrapping basic player logic like queuing and
generating random content.
"""

import json

from fm.ext import config, redis
from fm.models.spotify import Track
from sqlalchemy.sql import func


class Queue(object):
    """
    A class wraps a player queue logic. Class provides simple and atomic
    operations to a redis instance.
    """
    @staticmethod
    def add(track, user):
        """ Add a track into a redis queue

        Parameters
        ----------
        track: fm.models.spotify.Track
            intance of Track which is added into queue
        user: fm.models.user.User
            user who adds a track into queue
        """
        redis.rpush(
            config.PLAYLIST_REDIS_KEY,
            json.dumps({
                'uri': track.spotify_uri,
                'user': user.id
            })
        )

        redis.publish(config.PLAYER_CHANNEL, json.dumps({
            'event': 'add',
            'uri': track.spotify_uri,
            'user': user.id
        }))

    @staticmethod
    def length():
        """ Return list of messages in a redis playlist queue

        Return
        ------
        int
            number of items in a playlist queue
        """
        return redis.llen(config.PLAYLIST_REDIS_KEY)


class Random(object):
    """
    A class generates random content
    """
    @staticmethod
    def get_tracks(count=1):
        """ Returns a list of random tracks from already played ones

        Parameters
        ----------
            count: int
                Length of generated list of tracks. Default is 1.

        Returns
        -------
        list
            Random tracks of fm.models.spotify.Track
        """
        return Track.query.order_by(func.random()).limit(count).all()
