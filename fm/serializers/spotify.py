#!/usr/bin/env python
# encoding: utf-8

"""
fm.serializers.spotify
======================

Kim serializers for `fm.models.spotify` models.
"""

import kim.types as t

from kim.fields import Field
from kim.contrib.sqa import SQASerializer


class AlbumSerializer(SQASerializer):
    """
    """

    pass


class TrackSerialzier(SQASerializer):
    """
    """

    name = Field(t.String, required=True)
    duration = Field(t.Integer, required=True)
