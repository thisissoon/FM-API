#!/usr/bin/env python
# encoding: utf-8

"""
fm.http.pagination
==================

Helper classes for constructing paginated responses.
"""

from flask import request
from functools import wraps
from furl import furl
from math import ceil
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

            response = function(
                self,
                limit=args['limit'],
                page=args['page'],
                offset=(args['page'] - 1) * args['limit'],
                *args,
                **kwargs)

            return response

        return wrapper

    return decorator


class Pagination(object):
    """ A helper class to generate pagination links for the Link header
    in the response.

    Example
    -------

        >>> from fm.http.pagination import Pagination
        >>> Pagination(10, 100, 10).headers()
        {
            'Link': '<http://foo.com?limit=10&page=10>; rel="first", ...'
            'Pagination-Count': 100,
            'Pagination-Total': 10
        }

    """

    def __init__(self, limit, total, page):
        """ Constructor.

        Arguments
        ---------
        limit : int
            Number of items returned on each page
        total : int
            Total number of items
        page : int
            The current page
        """

        self.limit = limit
        self.total = total
        self.page = page

    def headers(self):
        """ Generates the dictionary to be be passed into the response
        headers.

        Returns
        -------
        dict
            The header dictionary
        """

        links = []

        if self.has_first:
            links.append(self.first_url)

        if self.has_prev:
            links.append(self.prev_url)

        if self.has_next:
            links.append(self.next_url)

        if self.has_last:
            links.append(self.last_url)

        headers = {
            'Pagination-Count': self.total,
            'Pagination-Pages': self.pages
        }

        if len(links) > 0:
            headers.update({
                'Link': ', '.join(links),
            })

        return headers

    def make_link(self, page, rel):
        """ Generates the url to be used in the ``Link`` header, amending
        the current request url with page number and limit for the url.

        Example
        -------

            >>> from fm.http.pagination import Pagination
            >>> p = Pagination(1, 10, 1)
            >>> p.make_link(2, 'next')
            u'<http://foo.com?limit=1&page=2>; rel="next"'

        """

        f = furl(request.url)
        f.args['page'] = page
        f.args['limit'] = self.limit

        link = u'<{0}>; rel="{1}"'.format(f.url, rel)

        return link

    @property
    def pages(self):
        """ Calculates the total number of pages from the total count and
        number of items per page.

        Retuens
        -------
        int
            Total number of pages
        """

        if self.limit == 0:
            return 0

        return int(ceil(self.total / float(self.limit)))

    @property
    def has_first(self):
        """ Calculates if a first page link should be shown.

        Returns
        -------
        bool
        """

        return self.page > 2

    @property
    def first_url(self):
        """ Generates the first page url for the ``Link`` header.

        Returns
        -------
        str
            The link
        """

        return self.make_link(1, 'first')

    @property
    def has_prev(self):
        """ Calculates if the previous page link should be shown.

        Returns
        -------
        bool
        """

        return self.page > 1

    @property
    def prev_url(self):
        """ Generates the previous page url for the ``Link`` header.

        Returns
        -------
        str
            The link
        """

        return self.make_link(self.page - 1, 'prev')

    @property
    def has_next(self):
        """ Calculates if we have a next page.

        Returns
        -------
        bool
        """

        return self.page < self.pages

    @property
    def next_url(self):
        """ Generates the next page url for the ``Link`` header.

        Returns
        -------
        str
            The link
        """

        return self.make_link(self.page + 1, 'next')

    @property
    def has_last(self):
        """ Calculates if we should show a last page

        Returns
        -------
        bool
        """

        return self.page < (self.pages - 2)

    @property
    def last_url(self):
        """ Generates the last page url for the ``Link`` header.

        Returns
        -------
        str
            The link
        """

        return self.make_link(self.pages, 'last')
