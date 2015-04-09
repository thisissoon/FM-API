import httplib

import requests
from flask import url_for


class SpotifyApi(object):

    class UnauthorizedException(Exception):
        pass

    def __init__(self, user):
        self.user = user

    def playlist_iterator(self):
        """
        Iterate though user's playlists. Function uses Spotify internal
        pagination to move to another page.
        """
        nxt_playlist = self.playlist_url
        while nxt_playlist is not None:
            playlists_data = self._get_user_playlist(nxt_playlist)
            nxt_playlist = playlists_data['next']
            for playlist in playlists_data['items']:
                yield Playlist(self.user, playlist)

    @property
    def playlist_url(self):
        """
        Returns spotify endpoint for user's playlists
        """
        return ('https://api.spotify.com/v1/users/{userid}/playlists' +
                '?offset=0&limit=20').format(userid=self.user.spotify_id)


    def _get_user_playlist(self, url):
        """
        Function handle user Spotify authorization and return raw response
        data in following structure.
        {
            "href": "https://api.spotify.com/v1/users/8/playlists",
            "items": [],
            "limit": 3,
            "next": "https://api.spotify.com/v1/users/8/playlists?offset=3&..",
            "offset": 0,
            "previous": null,
            'total": 6
        }
        """
        response = requests.get(url, headers={
            'authorization': 'Bearer {access_token}'.format(
                access_token=self.user.spotify_credentials['access_token'])
            }
        )
        if response.status_code == httplib.UNAUTHORIZED:
            raise SpotifyApi.UnauthorizedException()
        return response.json()

    def get_playlists_tracks(self, playlist_id):
        pass


class Playlist(object):
    """ Playlist class is skeleton for Spotify playlist serializers
    """

    class Tracks(object):
        """ Nested object which points to tracks in playlist and expose number
        of tracks in it.
        """

        def __init__(self, user, total, playlist_id):
            self.total = total
            self.playlist = url_for('users.user_spotify_track',
                                    user_pk=user.id,
                                    playlist_pk=playlist_id,
                                    _external=True)

    def __init__(self, user, playlist_data):
        self.id = playlist_data['id']
        self.name = playlist_data['name']
        self.tracks = Playlist.Tracks(
            user=user,
            total=playlist_data['tracks']['total'],
            playlist_id=playlist_data['id']
        )
