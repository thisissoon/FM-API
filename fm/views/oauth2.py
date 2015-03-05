#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.oauth2
===============

Views for the Google OAUTH2 authentication.
"""

from flask import current_app, render_template
from flask.views import MethodView
from fm import http


class TestFrontendView(MethodView):
    """ This view should only be accessible in DEBUG mode.
    """

    def get(self):
        """
        """

        if current_app.debug == False:
            return http.NotFound()

        return render_template('oauth2.html')
