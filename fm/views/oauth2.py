#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.oauth2
===============

Views for the Google OAUTH2 authentication.
"""

# Standard Libs
import json

# Third Party Libs
from flask import current_app, render_template, request, url_for
from flask.views import MethodView
from furl import furl

# First Party Libs
from fm import http
from fm.ext import db
from fm.logic.oauth import authorize_spotify_user
from fm.models.user import User
from fm.oauth2.google import GoogleOAuth2Exception, authenticate_oauth_code
from fm.oauth2.spotify import SpotifyOAuth2Exception
from fm.session import current_user, make_session, session_only_required


class GoogleTestClientView(MethodView):
    """ This view should only be accessible in DEBUG mode.
    """

    def get(self):
        """ Renders a HTML test client for testing google OAuth2 Flow
        """

        if current_app.debug is False:
            return http.NotFound()

        return render_template('oauth2/google.html')


class SpotifyTestClientView(MethodView):
    """ This view should only be accessible in DEBUG mode.
    """

    def get(self):
        """ Renders a HTML test client for testing google OAuth2 Flow
        """
        if current_app.debug is False:
            return http.NotFound()

        return render_template('oauth2/spotify.html')


class GoogleConnectView(MethodView):
    """ View for handling Google OAuth2 account connections.
    """

    def post(self):
        """ Called on a successfull OAuth2 flow. The request should contain
        a JSON body with a single token attribute which will exchanged
        for a long lived token. This is our defacto Login resource.
        """

        # OAuth Code Validation
        try:
            result, credentials = authenticate_oauth_code(
                request.json['code'],
                request.headers.get('ORIGIN'))
        except GoogleOAuth2Exception as e:
            return http.UnprocessableEntity(errors={
                'code': [
                    e.message
                ]
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
            headers.update({
                'Location': url_for('users.user', pk=user.id, _external=True)
            })

        # Create a session for subsequent requests
        session_id = make_session(user.id)

        return response_class(
            {
                'access_token': session_id
            },
            headers=headers)


class SpotifyConnectView(MethodView):

    @session_only_required
    def get(self):
        try:
            code = request.args['code']
        except KeyError:
            return http.BadRequest('Paramether `code` is missing')
        try:
            authorize_spotify_user(current_user, code)
        except SpotifyOAuth2Exception as e:
            return http.Unauthorized(e.message)

        return ''
