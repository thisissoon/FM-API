#!/usr/bin/env python
# encoding: utf-8

"""
fm.http.pagination
==================

Helper classes for constructing paginated responses.
"""

from flask import request
from functools import wraps
from webargs import Arg
from webargs.flaskparser import FlaskParser


def paginate(limit=20, maximum=50):
    """ Paginate decorator. This decorator marks a resource that supports
    pagination and passed 3 keyword arguments to the decorated function, these
    are:

    * ``limit``: The number of records per page - default 20
    * ``page``: The current page requested -  defualt 1
    * ``offset``: The offset to be used in queries to get the correct rows

    These can then be used to in queries to limit the result set.

    Keyword Arguments
    -----------------
    limit : int, default 20
        The default limit to be used, this can be overriden by a query param
        of the same name
    maximum : int, default 50
        The maximum number of rows per page
    """

    def decorator(function):

        @wraps(function)
        def wrapper(self, *args, **kwargs):

            args = FlaskParser().parse({
                'page': Arg(int, default=1),
                'limit': Arg(int, default=limit)
            }, request)

            if args['limit'] > maximum:
                args['limit'] = maximum

            return function(
                self,
                limit=args['limit'],
                page=args['page'],
                offset=(args['page'] - 1) * args['limit'],
                *args,
                **kwargs)

        return wrapper

    return decorator


class Pagination(object):

    def __init__(self, response_class, query, **kwargs):
        """ Constructor, takes the original response from the view,
        the query to return the total item count. Optional keyword
        arguments include `limit`, `offset` and `page`.
        """

        self.limit = kwargs.pop('limit', 50)
        self.offset = kwargs.pop('offset', 0)
        self.page = kwargs.pop('page', 1)

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
