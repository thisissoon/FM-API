from flask import url_for
from fm.models.user import User
from kim import types


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
        return url_for('users.user_playlists', pk=value, _external=True)
