#!/usr/bin/env python
# encoding: utf-8

"""
fm.views.track
==============

Track resources.
"""


from flask.views import MethodView
from fm import http
from fm.models.spotify import Track
from fm.serializers.spotify import TrackSerialzier


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

    def get(self, pk):
        """ Returns a single track object by primary key, if the track does
        not exist a 404 will be returned.

        Arguments
        ---------
        pk : str
            The track primary key
        """

        track = Track.query.get(pk)
        if track is None:
            return http.NotFound()

        return http.OK(TrackSerialzier().serialize(track))
