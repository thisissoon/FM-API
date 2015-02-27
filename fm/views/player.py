#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.player
===============

Views for handling /player API resource requests.
"""

import json

from flask import current_app
from flask.views import MethodView
from fm.ext import redis


class Tracks(MethodView):
    """ The Player resource allows for the management of the playlist and
    the current playing track.
    """

    def get(self):
        """ Returns the current tracks in the playlist.
        """

        pass

    def post(self):
        """ Allows you to add a new track to the player playlist.
        """

        channel = current_app.config.get('PLAYER_CHANNEL')
        redis.publish(channel, json.dumps({
            'event': 'play',
            'track': 'spotify:track:67WTwafOMgegV6ABnBQxcE'}))

        return json.dumps({'code': 200})

    def put(self):
        """ Allows for updates to a playing track. This resource can be
        used to pause and resume the playing track.
        """

        pass

    def delete(self):
        """ Allows for a track to be unloaded by the player. This can be any
        player in the playlist.
        """

        pass
