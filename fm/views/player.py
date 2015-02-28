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
from fm.ext import config, redis
from webargs import Arg, ValidationError
from webargs.flaskparser import FlaskParser


class Pause(MethodView):
    """ The pause resources allows the payer to paused and unpaused via
    POST for pause and DELTETE to unpause the player.
    """

    def post(self):
        """ Pauses the player.
        """

        redis.publish(config.PLAYER_CHANNEL, json.dumps({'event': 'pause'}))

        return json.dumps({'code': 201})

    def delete(self):
        """ Unapuses the player.
        """

        redis.publish(config.PLAYER_CHANNEL, json.dumps({'event': 'resume'}))

        return json.dumps({'code': 204})


class Tracks(MethodView):
    """ The Track resource allows for the management of the playlist.
    """

    def post(self):
        """ Allows you to add anew track to the player playlist.
        """

        try:
            args = FlaskParser().parse({
                'track': Arg(str, required=True)
            }, request)
        except ValidationError as err:
            return json.dumps({'error': str(err),  'code': 400})

        redis.rpush('playlist', args.get('track'))

        return json.dumps({'code': 200})
