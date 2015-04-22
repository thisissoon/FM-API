# Third Pary Libs
from flask import url_for
from kim import types

# First Party Libs
from fm.models.user import User


class SpotifyPlaylistEndpoint(types.String):
    """ A custom type for user's spotify playlists.
    Source must be set up for user id
    Example
    -------
        Field(types.SpotifyPlaylistEndpoint(), source='id')
    """

    def serialize_value(self, value):
        user = User.query.get(value)
        if user.spotify_id is None:
            return None
        return url_for('users.user_spotify_playlists', user_pk=value,
                       _external=True)
