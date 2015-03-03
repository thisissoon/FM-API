#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.player
===============

Views for handling /player API resource requests.
"""

import json

from flask import request
from flask.views import MethodView
from fm import http
from fm.ext import config, redis
from fm.serializers.player import PlaylistSchema


class Pause(MethodView):
    """ The pause resources allows the payer to paused and unpaused via
    POST for pause and DELTETE to unpause the player.
    """

    def post(self):
        """ Pauses the player.
        """

        redis.publish(config.PLAYER_CHANNEL, json.dumps({'event': 'pause'}))

        return http.Created()

    def delete(self):
        """ Unapuses the player.
        """

        redis.publish(config.PLAYER_CHANNEL, json.dumps({'event': 'resume'}))

        return http.NoContent()


class Playlist(MethodView):
    """ The Track resource allows for the management of the playlist.
    """

    def get(self):
        """ Returns a paginated list of tracks currently in the playlist.
        """

        tracks = redis.lrange('playlist', 0, -1)

        return http.OK(tracks or [])

    def post(self):
        """ Allows you to add anew track to the player playlist.
        """

        errors = PlaylistSchema().validate(request.json or {})
        if errors:
            return http.UnprocessableEntity(errors=errors)

        return http.Created()
