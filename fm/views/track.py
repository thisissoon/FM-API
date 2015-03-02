#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.track
==============

Track resources.
"""


from flask.views import MethodView
from fm import http


class Tracks(MethodView):
    """
    """

    def get(self):
        """
        """

        return http.OK()


class Track(MethodView):
    """
    """

    def get(self, pk):
        """
        """

        return http.OK()

    def put(self, pk):
        """
        """

        return http.OK()
