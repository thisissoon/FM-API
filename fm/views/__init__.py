#!/usr/bin/env python
# encoding: utf-8

"""
fm.views
========

Root View
"""

from flask.views import MethodView
from fm import http


class RootView(MethodView):
    """ Root View.
    """

    def get(self):
        """
        """

        return http.OK({
            'message': 'Welcome to the thisissoon.fm API',
        })
