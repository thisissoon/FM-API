#!/usr/bin/env python
# encoding: utf-8

"""
fm.models.user
==============

SQLAlchemy User Models.
"""

# Standard Libs
import uuid

# Third Party Libs
from sqlalchemy.dialects.postgresql import JSON, UUID

# First Party Libs
from fm.ext import db


class User(db.Model):
    """ Holds the registered users on the system.
    """

    __tablename__ = 'user'

    #
    # Keys
    #

    #: Primary Key - Our internal ID
    id = db.Column(UUID, primary_key=True, default=lambda: unicode(uuid.uuid4()))

    #: Google Plus ID
    gplus_id = db.Column(db.Unicode(128), nullable=False, index=True)

    #: Google OAuth Token
    oauth2_credentials = db.Column(JSON, nullable=False)

    #: Spotify Plus ID
    spotify_id = db.Column(db.Unicode(128), index=True)

    #: Spotify OAuth Token
    spotify_credentials = db.Column(JSON)

    #
    # Attributes
    #

    #: Email - Comes from Google
    email = db.Column(db.Unicode(128), nullable=False, index=True)

    #: Given Names
    given_name = db.Column(db.Unicode(128), nullable=False)

    #: Family Name
    family_name = db.Column(db.Unicode(128), nullable=False)

    #: Display Name
    display_name = db.Column(db.Unicode(128), nullable=False)

    #: Image URL
    avatar_url = db.Column(db.Text, nullable=False)
