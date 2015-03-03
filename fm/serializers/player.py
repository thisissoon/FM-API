#!/usr/bin/env python
# encoding: utf-8

"""
fm.serializers.player
=====================

Marshmallow schemas for player resources.
"""

from marshmallow import Schema, fields


class PlaylistSchema(Schema):
    """ This schema is used for adding tracks to the player playlist.
    """

    uri = fields.String(required=True)
