#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.oauth2
===============

Views for the Google OAUTH2 authentication.
"""

import httplib2

from apiclient.discovery import build
from flask import current_app, render_template, request
from flask.views import MethodView
from fm import http
from fm.ext import config
from oauth2client.client import credentials_from_code


class GoogleTestClientView(MethodView):
    """ This view should only be accessible in DEBUG mode.
    """

    def get(self):
        """ Renders a HTML test client for testing google OAuth2 Flow
        """

        if current_app.debug == False:
            return http.NotFound()

        return render_template('oauth2/google.html')


class GoogleConnectView(MethodView):
    """ View for handling Google OAuth2 account connections.
    """

    def post(self):
        """ Called on a successfull OAuth2 flow. The request should contain
        a JSON body with a single token attribute which will exchanged
        for a long lived token.
        """

        service = build('plus', 'v1')

        credentials = credentials_from_code(
            config.GOOGLE_CLIENT_ID,
            config.GOOGLE_CLIENT_SECRET,
            '',
            request.json['token'])

        h = httplib2.Http()
        h = credentials.authorize(h)

        grequest = service.people().get(userId='me')
        result = grequest.execute(http=h)

        if not result['domain'] in config.GOOGLE_ALLOWED_DOMAINS:
            # Disconnect the App Straight Away
            access_token = credentials.access_token
            url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
            h = httplib2.Http()
            h.request(url, 'GET')
            # Return a sane error
            return http.UnprocessableEntity(errors={
                'token': ['Only Members of SOON_ or This Here can Login']
            })

        return http.OK()
