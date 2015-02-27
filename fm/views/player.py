#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.player
===============

Views for handling /player API resource requests.
"""

from flask.views import MethodView


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

        pass

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
