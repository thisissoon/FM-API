import json

from fm.ext import config, redis
from fm.models.spotify import Track
from sqlalchemy.sql import func


class Queue(object):

    @staticmethod
    def add(track, user):
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


class Random(object):

    @staticmethod
    def get_tracks(count=1):
        return Track.query.order_by(func.random()).limit(count).all()
