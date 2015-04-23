# First Party Libs
from fm.ext import db
from fm.oauth2.spotify import SpotifyOAuth2


def authorize_spotify_user(user, code):
    user_data, credentials = SpotifyOAuth2.authenticate_oauth_code(code)
    user.spotify_id = user_data['id']
    user.spotify_credentials = credentials
    db.session.add(user)
    db.session.commit()


def update_spotify_credentials(user):
    user.spotify_credentials = SpotifyOAuth2.refresh_access_token(
        user.spotify_credentials['refresh_token']
    )
    db.session.add(user)
    db.session.commit()
