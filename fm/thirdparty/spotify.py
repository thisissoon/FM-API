import httplib

import requests


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
                yield Playlist(playlist)

    @property
    def playlist_url(self):
        """
        Returns spotify endpoint for user's playlists
        """
        return 'https://api.spotify.com/v1/users/{userid}/playlists?offset=0&limit=3'.format(
            userid=self.user.spotify_id
        )

    def _get_user_playlist(self, url):
        """
        Function handle user Spotify authorization and return raw response
        data in following structure.
        {
            "href": "https://api.spotify.com/v1/users/8/playlists?offset=0&limit=3",
            "items": [],
            "limit": 3,
            "next": "https://api.spotify.com/v1/users/8/playlists?offset=3&limit=3",
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

    def __init__(self, playlist_json):
        self.playlist_json = playlist_json
        self.name = self.playlist_json['name']
        self.href = self.playlist_json['href']
        self.id = self.playlist_json['id']
        self.images = self.playlist_json['images']
        self.tracks_url = self.playlist_json['tracks']['href']

    @property
    def tracks(self):
        pass

    # {
    #   "collaborative": false,
    #   "external_urls": {
    #     "spotify": "http://open.spotify.com/user/spotify/playlist/6kxQr8LTtln4Li4dnT6N0B"
    #   },
    #   "href": "https://api.spotify.com/v1/users/spotify/playlists/6kxQr8LTtln4Li4dnT6N0B",
    #   "id": "6kxQr8LTtln4Li4dnT6N0B",
    #   "images": [
    #     {
    #       "height": 300,
    #       "url": "https://i.scdn.co/image/1e8bde54412651f631811288ebb2036615a32010",
    #       "width": 300
    #     }
    #   ],
    #   "name": "Running Motivation",
    #   "owner": {
    #     "external_urls": {
    #       "spotify": "http://open.spotify.com/user/spotify"
    #     },
    #     "href": "https://api.spotify.com/v1/users/spotify",
    #     "id": "spotify",
    #     "type": "user",
    #     "uri": "spotify:user:spotify"
    #   },
    #   "public": true,
    #   "tracks": {
    #     "href": "https://api.spotify.com/v1/users/spotify/playlists/6kxQr8LTtln4Li4dnT6N0B/tracks",
    #     "total": 39
    #   },
    #   "type": "playlist",
    #   "uri": "spotify:user:spotify:playlist:6kxQr8LTtln4Li4dnT6N0B"
    # }
