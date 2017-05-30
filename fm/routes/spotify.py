#!/usr/bin/env python
# encoding: utf-8

"""
fm.routes.spotify
================

Spotify API routes.
"""

# Third Party Libs
from flask.ext.via.routers.default import Pluggable

# First Party Libs
from fm.views import spotify


routes = [
    Pluggable('/search', spotify.SearchView, 'search'),
    Pluggable('/artist/<id>', spotify.ArtistView, 'artist'),
    Pluggable('/artist/<id>/albums', spotify.ArtistAlbumView, 'artist.alums'),
]
