#!/usr/bin/env python
# encoding: utf-8

"""
fm.db.model
===========

SQLAlchemy models.
"""

import datetime

from dateutil.tz import tzutc
from sqlalchemy import Column
from fm.db.types import UTCDateTime
from flask.ext.sqlalchemy import Model


class FMModel(Model):
    """ Base model for all FM models.
    """

    #: Always store a created date
    created = Column(
        UTCDateTime,
        index=True,
        nullable=False,
        default=lambda: datetime.datetime.now(tzutc()))

    #: Always store an update date
    updated = Column(
        UTCDateTime,
        index=True,
        nullable=False,
        default=lambda: datetime.datetime.now(tzutc()),
        onupdate=lambda: datetime.datetime.now(tzutc()))