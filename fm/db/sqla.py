#!/usr/bin/env python
# encoding: utf-8

"""
fm.fb.sqla
==========

Custom SQLAlchemy functionality.
"""
# Third Party Libs
from flask.ext.sqlalchemy import (
    SQLAlchemy,
    _BoundDeclarativeMeta,
    _QueryProperty,
    declarative_base
)

# First Party Libs
from fm.db.model import FMModel


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
