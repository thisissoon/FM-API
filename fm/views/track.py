#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.track
==============

Track resources.
"""

import uuid

from fm.serializers.spotify import TrackSerialzier
from fm.models.spotify import Track
from flask.views import MethodView
from fm import http


class TracksView(MethodView):
    """ Operates on the Track collection.
    """

    @http.pagination.paginate()
    def get(self, *args, **kwargs):
        """ Returns a paginated list of tracks stored in our DB.
        """

        total = Track.query.count()
        rows = Track.query \
            .limit(kwargs.get('limit')) \
            .offset(kwargs.get('offset')) \
            .all()

        return http.OK(
            TrackSerialzier().serialize(rows, many=True),
            limit=kwargs.get('limit'),
            page=kwargs.get('page'),
            total=total)


class TrackVeiw(MethodView):
    """ Operates on a single track object.
    """

    def get(self, pk_or_uri):
        """ Returns a single track object by primary key, if the track does
        not exist a 404 will be returned.

        Arguments
        ---------
        pk : str
            The track primary key
        """

        try:
            uuid.UUID(pk_or_uri, version=4)
        except ValueError:
            field = Track.spotify_uri
        else:
            field = Track.id

        track = Track.query.filter(field == pk_or_uri).first()
        if track is None:
            return http.NotFound()

        return http.OK(TrackSerialzier().serialize(track))
