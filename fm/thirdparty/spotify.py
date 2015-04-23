#!/usr/bin/env python
# encoding: utf-8

# Standard Libs
import httplib

# Third Pary Libs
import requests
from flask import url_for
from kim import types as t
from kim.fields import Field
from kim.serializers import Serializer


class BaseSpotifySerializer(Serializer):

    id = Field(t.String)
    name = Field(t.String)
    spotify_uri = Field(t.String)


class PlaylistSerializer(BaseSpotifySerializer):
    """ Spotify playlist serializer

    Returns following data s structure:
        {
            'id': '4wtLaWQcPct5tlAWTxqjMD',
            'name': 'The Happy Hipster',
            'tracks': {
                'playlist': url to user's spotify tracks,
                'total': 186
            }
        }
    """

    class TrackSerializer(Serializer):
        """ Nested Track serializer
        Exposing url for tracks in playlist and total number of tracks in it
        """
        total = Field(t.Integer)
        playlist = Field(t.String)

    tracks = Field(t.Nested(TrackSerializer()))


class TrackSerializer(BaseSpotifySerializer):
    """ Spotify track serializer
    """

    class Album(BaseSpotifySerializer):
        pass

    class Artists(BaseSpotifySerializer):
        pass

    duration = Field(t.Integer)  # ms
    album = Field(t.Nested(Album()))
    artists = Field(t.Collection(t.Nested(Artists())))


class SpotifyApi(object):

    class UnauthorizedException(Exception):
        pass

    def __init__(self, user):
        self.user = user

    def playlist_iterator(self):
        """
        Iterate though user's playlists. Function uses Spotify internal
        pagination to move to another page.

        Data structure returned from Spotify playlist endpoint
        ------------------------------------------------------
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
        nxt_playlist = self.playlist_url
        while nxt_playlist is not None:
            playlists_data = self._hit_spotify_api(nxt_playlist)
            nxt_playlist = playlists_data['next']
            for playlist in playlists_data['items']:
                yield Playlist(self.user, playlist)

    @property
    def playlist_url(self):
        """
        Returns spotify endpoint for user's playlists
        """
        return 'https://api.spotify.com/v1/users/{user_id}/playlists'.format(
            user_id=self.user.spotify_id)

    def get_playlists_tracks_url(self, playlist_id):
        """
        Returns spotify endpoint for user's tracks
        """
        track_url = ('https://api.spotify.com/v1/users/{user_id}/playlists/' +
                     '{playlist_id}/tracks')
        return track_url.format(
            user_id=self.user.spotify_id,
            playlist_id=playlist_id
        )

    def _hit_spotify_api(self, url):
        """
        Function handle user Spotify authorization and return raw response
        data from Spotify api.
        """
        credentials = 'Bearer {access_token}'.format(
            access_token=self.user.spotify_credentials['access_token']
        )
        response = requests.get(url, headers={'authorization': credentials})
        if response.status_code == httplib.UNAUTHORIZED:
            raise SpotifyApi.UnauthorizedException()
        return response.json()

    def get_playlists_tracks(self, playlist_id):
        """
        Iterate though tracks in playlist. Function uses Spotify internal
        pagination to move to another page.

        Data structure returned from Spotify playlist endpoint
        ------------------------------------------------------
        {
            "href": "https://api.spotify.com/v1/users/6456/playlists/1kYVX1..",
            "items": [
                {
                    "added_at": "2015-04-08T11:44:18Z",
                    "added_by": {...},
                    "is_local": false,
                    "track": {
                        "album": {
                            "album_type": "album",
                            "available_markets": [],
                            "external_urls": {...},
                            "href": "https://api.spotify.com/v1/albums/7oyz..",
                            "id": "7oyz4rAEXqVz99kmWe3ejU",
                            "images": [...],
                            "name": "50 Film Classics",
                            "type": "album",
                            "uri": "spotify:album:7oyz4rAEXqVz99kmWe3ejU"
                        },
                        "artists": [
                            {
                                "external_urls": {...},
                                "href": "https://api.spotify.com/v1/artists..",
                                "id": "2uuAaf6yCHYDZDVCdMUlA3",
                                "name": "Klaus Tennstedt",
                                "type": "artist",
                                "uri": "spotify:artist:2uuAaf6yCHYDZDVCdMUlA3"
                            },
                            ...
                        ],
                        "available_markets": [],
                        "disc_number": 1,
                        "duration_ms": 106853,
                        "explicit": false,
                        "external_ids": {...},
                        "external_urls": {...},
                        "href": "https://api.spotify.com/v1/tracks/7rNIsIG0..",
                        "id": "7rNIsIG00EuyZZzLrVDNvg",
                        "name": "Strauss, R: Also sprach Zarathustra, Op. 3..",
                        "popularity": 40,
                        "preview_url": null,
                        "track_number": 1,
                        "type": "track",
                        "uri": "spotify:track:7rNIsIG00EuyZZzLrVDNvg"
                    }
                },
                ...
            ],
            "limit": 2,
            "next": "https://api.spotify.com/v1/users/6456/playlists/..",
            "offset": 0,
            "previous": null,
            "total": 6
        }
        """

        nxt_track = self.get_playlists_tracks_url(playlist_id)
        while nxt_track is not None:
            track_data = self._hit_spotify_api(nxt_track)
            nxt_track = track_data['next']
            for metadata in track_data['items']:
                yield Track(metadata['track'])


class BaseSpotify(object):

    def __init__(self, metadata):
        self.id = metadata['id']
        self.name = metadata['name']
        self.spotify_uri = metadata['uri']


class Playlist(BaseSpotify):
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
        super(Playlist, self).__init__(playlist_data)
        self.tracks = Playlist.Tracks(
            user=user,
            total=playlist_data['tracks']['total'],
            playlist_id=playlist_data['id']
        )


class Track(BaseSpotify):
    """ Track class is skeleton for Spotify track serializers
    """

    class Album(BaseSpotify):
        pass

    class Artists(BaseSpotify):
        pass

    def __init__(self, track_data):
        super(Track, self).__init__(track_data)
        self.duration = track_data['duration_ms']  # ms
        self.album = Track.Album(track_data['album'])
        self.artists = [Track.Album(art) for art in track_data['artists']]
