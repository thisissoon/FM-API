#!/usr/bin/env python
# encoding: utf-8

"""
tests.factories
===============

Base Factories and Types
"""

import factory
import uuid

from fm.ext import db
from sqlalchemy.types import Integer


class Factory(factory.Factory):
    """ All FM models will use UUID's rather than integers for their
    primary keys. This is not supported by FactoryBoy out of the box, this
    base class ensures that models with a UUID instead of an integer will
    function properly.
    """

    @classmethod
    def _setup_next_sequence(cls, *args, **kwargs):
        session = db.session
        model = cls._get_model_class()

        pk = getattr(model, model.__mapper__.primary_key[0].name)
        if isinstance(pk.type, Integer):
            max_pk = session.query(max(pk)).one()[0]
            if isinstance(max_pk, int):
                return max_pk + 1 if max_pk else 1

        return 1


class UUID4(factory.declarations.OrderedDeclaration):
    """ Custom factory boy type for generating UUIDs.
    """

    def evaluate(self, *args, **kwargs):
        """ Returns a UUID for use as an object primary key.
        """

        return uuid.uuid4()
