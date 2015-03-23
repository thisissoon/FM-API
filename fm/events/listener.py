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


def add_playlist_history(uri):
    """ Adds a track to the playlist history on a play event.

    Arguments
    ---------
    uri : str
        Spotify URI of the playing track
    """

    # Create Flask Application
    app = create()

    with app.app_context():
        track = Track.query.filter(Track.spotify_uri == uri).first()
        if track is not None:
            db.session.add(PlaylistHistory(track_id=track.id))
            db.session.commit()


def handle_event(message):
    """ Handles an event from the Redis Pubsub channel. If the event is one
    we care about we will spawn a new Greenlet to handle the event asynchronously.

    Argument
    --------
    event : dict
        The event data
    """

    if message['event'] == 'play':
        add_playlist_history(message['uri'])


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

    pubsub = redis.pubsub()
    pubsub.subscribe(config.PLAYER_CHANNEL)

    gevent.spawn(listen, pubsub).join()


if __name__ == '__main__':
    listener()
