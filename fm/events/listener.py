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


from fm.ext import config, redis
from gevent.monkey import patch_all


def handle_event(event):
    """ Handles an event from the Redis Pubsub channel. If the event is one
    we care about we will spawn a new Greenlet to handle the event asynchronously.

    Argument
    --------
    event : dict
        The event data
    """

    pass


def listen(pubsub):
    """ Listens for events on provided pubsub channel and spoawns other
    greenlets to act on them.
    """

    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            handle_event(data)


def listener():
    """ Redis event listener. Spawns a Gevent Greenlet which listens on the
    redis pubsub channel.
    """

    patch_all()

    pubsub = redis.pubsub()
    pubsub.subscribe(config.PLAYER_CHANNEL)

    gevent.spawn(listen, pubsub).join()
