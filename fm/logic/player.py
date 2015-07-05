"""
fm.logic.player
===========
Classes for handling and wrapping basic player logic like queuing and
generating random content.
"""

# Standard Libs
import json
import uuid

# Third Party Libs
from sqlalchemy.sql import func

# First Party Libs
from fm.ext import config, redis
from fm.models.spotify import Track


class Queue(object):
    """
    A class wraps a player queue logic. Class provides simple and atomic
    operations to a redis instance.
    """

    @staticmethod
    def add(uri, user):
        """ Add a track into a redis queue

        Parameters
        ----------
        uri: str
            The spotify URI of the Track to add to the Queue
        user: str
            The user id of the user whome added the track to the Queue
        """

        # Push the Track into the Queue
        redis.rpush(
            config.PLAYLIST_REDIS_KEY,
            json.dumps({
                'uri': uri,
                'user': user,
                'uuid': str(uuid.uuid4()),
            })
        )

        # Publish Add Event
        redis.publish(config.PLAYER_CHANNEL, json.dumps({
            'event': 'add',
            'uri': uri,
            'user': user
        }))

    @staticmethod
    def get_queue(offset=0, limit=None):
        if limit is None:
            limit = Queue.length()

        tracks = redis.lrange(
            config.PLAYLIST_REDIS_KEY, offset, (offset + limit - 1)
        )
        return (json.loads(track) for track in tracks)

    @staticmethod
    def get_tracks(offset=0, limit=None):
        """ Returns a list of Tracks in a queue. Default behaviour is to return
        all tracks in a queue - use limit to return desire number of tracks

        Parameters
        ----------
        offset: int
            Offset
        limit: int
            Limit

        """
        return (
            Track.query.filter(Track.spotify_uri == track['uri']).first()
            for track in Queue.get_queue(offset, limit)
        )

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
