#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.oauth2
===============

Views for the Google OAUTH2 authentication.
"""

import apiclient as google
import httplib2
import json

from flask import current_app, render_template, request, url_for
from flask.views import MethodView
from fm import http
from fm.ext import config, db
from fm.models.user import User
from fm.session import make_session
from furl import furl
from oauth2client.client import credentials_from_code, FlowExchangeError


class GoogleTestClientView(MethodView):
    """ This view should only be accessible in DEBUG mode.
    """

    def get(self):
        """ Renders a HTML test client for testing google OAuth2 Flow
        """

        if current_app.debug is False:
            return http.NotFound()

        return render_template('oauth2/google.html')


class GoogleConnectView(MethodView):
    """ View for handling Google OAuth2 account connections.
    """

    def post(self):
        """ Called on a successfull OAuth2 flow. The request should contain
        a JSON body with a single token attribute which will exchanged
        for a long lived token. This is our defacto Login resource.
        """

        from pdb import set_trace; set_trace()

        # Google Plus token validation
        service = google.discovery.build('plus', 'v1')

        try:
            credentials = credentials_from_code(
                config.GOOGLE_CLIENT_ID,
                config.GOOGLE_CLIENT_SECRET,
                '',
                request.json['code'],
                redirect_uri=config.GOOGLE_REDIRECT_URI)
        except FlowExchangeError as e:
            return http.UnprocessableEntity(errors={
                'code': ['Unable to authenticate with Google: {0}'.format(
                    e.message)]
            })

        h = httplib2.Http()
        h = credentials.authorize(h)

        grequest = service.people().get(userId='me')
        result = grequest.execute(http=h)

        # Can this user login
        if not result['domain'] in config.GOOGLE_ALLOWED_DOMAINS:
            # Disconnect the App Straight Away
            access_token = credentials.access_token
            url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
            h = httplib2.Http()
            h.request(url, 'GET')
            # Return a sane error
            return http.UnprocessableEntity(errors={
                'code': ['Only Members of SOON_ or This Here can Login']
            })

        # Default headers and response default response class for 200 OK
        headers = {}
        response_class = http.OK

        # Get the user from their Google+ ID
        user = User.query.filter(User.gplus_id == result['id']).first()

        # No User - Create a blank user object, set the response class to be
        # a 201
        if user is None:
            response_class = http.Created
            user = User()
            db.session.add(user)

        # Update User Date from Google
        user.gplus_id = result['id']
        user.oauth2_credentials = json.loads(credentials.to_json())
        user.email = result['emails'][0]['value']
        user.given_name = result['name']['givenName']
        user.family_name = result['name']['familyName']
        user.display_name = result['displayName']
        user.avatar_url = furl(result['image']['url']).remove(['sz']).url

        # Save Changes
        db.session.commit()

        # New user - return a Location Header with url to resource
        if response_class == http.Created:
            location = furl(request.url_root) \
                .set(path=url_for('users.user', pk=user.id))
            headers.update({
                'Location': location.url
            })

        # Create a session for subsequent requests
        session_id = make_session(user.id)
        headers.update({
            'Auth-Token': session_id
        })

        return response_class(headers=headers)
