#!/usr/bin/env python
# encoding: utf-8

"""
fm.fb.sqla
==========

Custom SQLAlchemy functionality.
"""

from fm.db.model import FMModel
from flask.ext.sqlalchemy import (
    declarative_base,
    SQLAlchemy,
    _BoundDeclarativeMeta,
    _QueryProperty)


class FMSQLAlchemy(SQLAlchemy):

    def make_declarative_base(self):
        """ Creates the declarative base.
        """

        base = declarative_base(
            cls=FMModel,
            name='Model',
            metaclass=_BoundDeclarativeMeta)
        base.query = _QueryProperty(self)

        return base
