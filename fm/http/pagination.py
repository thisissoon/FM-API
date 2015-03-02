#!/usr/bin/env python
# encoding: utf-8

"""
fm.http.pagination
==================

Helper classes for constructing paginated responses.
"""

from flask import request
from webargs import Arg
from webargs.flaskparser import FlaskParser


class Pagination(object):

    def __init__(self, response_class, query, **kwargs):
        """ Constructor, takes the original response from the view,
        the query to return the total item count. Optional keyword
        arguments include `limit`, `offset` and `page`.
        """

        self.limit = kwargs.pop('limit', 50)
        self.offset = kwargs.pop('offset', 0)
        self.page = kwargs.pop('page', 1)

        headers = kwargs.pop('headers', {})
        status = kwargs.pop('status', None)

        query = self.paginate_query(query)

        return response_class()

    def paginate_query(self, query):
        """
        """

        args = FlaskParser().parse({
            'page': Arg(int, default=1),
            'limit': Arg(int, default=50)
        }, request)

        query = query \
            .limit(args['limit']) \
            .offset((args['page'] - 1) * args['limit'])

        return query
