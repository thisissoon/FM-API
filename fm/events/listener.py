#!/usr/bin/env python
# encoding: utf-8

"""
fm.events.listener
==================

Redis Pub/Sub Service, listening on events from a Redis channel and
handling events it cares about.
"""

import gevent
import json


from fm.app import create
from fm.ext import config, db, redis
from fm.models.spotify import Track, PlaylistHistory
from fm.models.user import User
from gevent.monkey import patch_all


def add_playlist_history(uri, user):
    """ Adds a track to the playlist history on a play event.

    Arguments
    ---------
    uri : str
        Spotify URI of the playing track
    user : str
        The Users primary key
    """

    track = Track.query.filter(Track.spotify_uri == uri).first()
    user = User.query.filter(User.id == user).first()
    if track is not None and User is not None:
        db.session.add(PlaylistHistory(
            track_id=track.id,
            user_id=user.id
        ))
        db.session.commit()


def handle_event(message):
    """ Handles an event from the Redis Pubsub channel. If the event is one
    we care about we will spawn a new Greenlet to handle the event asynchronously.

    Argument
    --------
    event : dict
        The event data
    """

    # Create Flask Application
    app = create()

    with app.app_context():
        if message['event'] == 'end':
            add_playlist_history(message['uri'], message['user'])


def listen(pubsub):
    """ Listens for events on provided pubsub channel and spoawns other
    greenlets to act on them.

    Arguments
    ---------
    pubsub : redis.client.PubSub
        The redis pubsub instance
    """

    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            gevent.spawn(handle_event, data)


def listener():
    """ Redis event listener. Spawns a Gevent Greenlet which listens on the
    redis pubsub channel. This is the entrypoint for
    ``manage.py runeventlistener``.
    """

    patch_all()

    pubsub = redis.pubsub()
    pubsub.subscribe(config.PLAYER_CHANNEL)

    gevent.spawn(listen, pubsub).join()


if __name__ == '__main__':
    listener()
