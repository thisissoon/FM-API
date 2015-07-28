#!/usr/bin/env python
# encoding: utf-8

"""
fm.tasks.track
=================

Asynchronous tasks specifically relating to Tracks.
"""

# First Party Libs
from fm.ext import celery
from fm.models.spotify import Track
from fm.thirdparty.echonest import EchoNestError, get_track_analysis


@celery.task
def update_analysis(pk):
    """ Task for updating an existing tracks analysis asynchronously from
    Echo Nest.

    pk : str
        The UUID Primary Key of the Track
    """

    track = Track.query.get(pk)
    if track is None:
        # TODO: Log This
        return False

    # Call Echo Nest
    try:
        analysis = get_track_analysis(track.spotify_uri)
    except EchoNestError:
        # TODO: Log This
        return False

    # commit analysis data to track
    analysis

    return True
