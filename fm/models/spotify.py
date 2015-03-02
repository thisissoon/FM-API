#!/usr/bin/env python
# encoding: utf-8

"""
fm.models.tracks
================

Models for storing Spotify Track data.
"""

from fm.ext import db
from sqlalchemy.dialects.postgresql import UUID


class SpotifyTrack(db.Model):

    id = db.Column(UUID, primary_key=True)
    spotify_id = db.Column(db.Unicode(128), unique=True, nullable=False, index=True)
