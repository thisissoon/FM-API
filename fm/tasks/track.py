#!/usr/bin/env python
# encoding: utf-8

"""
fm.tasks.track
==============

Celery tasks relating to Spotify track data.
"""


from fm.ext import celery


@celery.task(bind=True)
def track_data_from_spotify(self, uri):
    pass
