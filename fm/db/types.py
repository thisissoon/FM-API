#!/usr/bin/env python
# encoding: utf-8

"""
fm.db.types
===========

Custom types for SQLAlchemy models.
"""

# Standard Libs
from datetime import datetime

# Third Party Libs
from dateutil.tz import tzutc
from sqlalchemy import types


class UTCDateTime(types.TypeDecorator):
    """ Use this type to ensure a UTC datetime object is always stored in the
    database.
    """

    impl = types.DateTime

    def process_bind_param(self, value, engine):
        if value is not None:
            return value.astimezone(tzutc())

    def process_result_value(self, value, engine):
        if value is not None:
            return datetime(
                value.year,
                value.month,
                value.day,
                value.hour,
                value.minute,
                value.second,
                value.microsecond,
                tzinfo=tzutc())
