#!/usr/bin/env python
# encoding: utf-8

"""
fm.oauth2.google
=========

Google oAuth2 Connection helper methods.
"""
# Third Party Libs
import apiclient
import httplib2
from oauth2client.client import FlowExchangeError, credentials_from_code

# First Party Libs
from fm.ext import config


class GoogleOAuth2Exception(Exception):
    """ Custom Exception class to raise when errors are detected during
    the authentication flow.
    """

    pass


def get_credentials(code):
    """ Creates a google oauth2 client credentials instance, validating
    the provided token with google.

    Arguments
    ---------
    code : str
        The oAuth2 code from the webflow

    Raises
    ------
    GoogleOAuth2Exception
        When an errors occures during token validation

    Returns
    -------
    oauth2client.client.OAuth2Credentials
        Google oAuth2 client credentials instance
    """

    try:
        credentials = credentials_from_code(
            config.GOOGLE_CLIENT_ID,
            config.GOOGLE_CLIENT_SECRET,
            '',
            code,
            redirect_uri=config.GOOGLE_REDIRECT_URI)
    except FlowExchangeError as e:
        raise GoogleOAuth2Exception(
            'Problem authenticating with Google: {0}'.format(e.message))

    return credentials


def user_from_credentials(credentials):
    """ Gets the authenticated user data from Google+.

    Arguments
    ---------
    credentials : oauth2client.client.OAuth2Credentials
        Google oAuth2 client credentials instance

    Returns
    -------
    dict
        The user data from Google+
    """

    http = httplib2.Http()
    http = credentials.authorize(http)

    service = apiclient.discovery.build('plus', 'v1')
    request = service.people().get(userId='me')

    user = request.execute(http=http)

    return user


def disconnect(access_token):
    """ Disconnects a user fropm the application.

    Arguments
    ---------
    access_token : str
        The users credentials access token

    Raises
    ------
    GoogleOAuth2Exception
        When an error occurs disconnecting the user form the application
    """

    url = 'https://accounts.google.com/o/oauth2/revoke?token={0}'.format(
        access_token)

    request = httplib2.Http()
    response = request.request(url, 'GET')

    if not response[0]['status'] == '200':
        raise GoogleOAuth2Exception('Unable to disconnect application')


def authenticate_oauth_code(code):
    """ Authenticates the users web flow oAuth2 code with Google returning
    the authenticated users Google+ data to be stored in the system.

    Arguments
    ---------
    code : str
        The oAuth2 code from the webflow

    Raises
    ------
    GoogleOAuth2Exception
        When the user is not permitted to use the application - must be
        in the allowed domains

    Returns
    -------
    tuple
        The user data from Google+ and Credentials instance
    """

    credentials = get_credentials(code)
    user = user_from_credentials(credentials)

    if not user['domain'] in config.GOOGLE_ALLOWED_DOMAINS:
        disconnect(credentials.access_token)
        raise GoogleOAuth2Exception('You need be a member of SOON_ or This Here')

    return user, credentials
