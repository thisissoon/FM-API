#!/usr/bin/env python
# encoding: utf-8

"""
fm.http
=======

Classes for returning HTTP responses.
"""

import json


from .pagination import Pagination

from flask import request
from furl import furl
from werkzeug.wrappers import Response as ResponseBase


class Response(ResponseBase):
    """ Base Response Object. This overrides the default in Flask, set in the
    application factory
    """

    default_mimetype = 'application/json; charset=utf-8'
    default_headers = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubdomains; preload'
    }

    def __init__(self, response=None, *args, **kwargs):
        """ Overrides default response constructor, automaticall turning the
        response data into a JSON object and setting default headers.
        """

        headers = kwargs.pop('headers', {})
        status = kwargs.pop('status', None)

        limit = kwargs.pop('limit', None)
        page = kwargs.pop('page', None)
        total = kwargs.pop('total', None)

        if all([limit, page, total]):
            headers.update(Pagination(limit, total, page).headers())

        # Update passed headers with the default headers
        headers.update(self.default_headers)

        if response is not None:
            response = json.dumps(response)

        return super(ResponseBase, self).__init__(
            response,
            headers=headers,
            status=status,
            *args,
            **kwargs)


class OK(Response):
    """ Return a standard HTTP 200 Response.

    Example
    -------
        >>> from fm import http
        >>> response = http.OK({'foo': 'bar'})

    """

    default_status = 200


class Created(Response):
    """ Return a standard HTTP 201 Response. Remember to add a `Location`
    header with a url to the newly created resource if applicable.

    Example
    -------
        >>> from fm import http
        >>> response = http.Created(headers={'Location': 'http://...'})

    """

    default_status = 201

    def __init__(self, *args, **kwargs):
        """
        """

        location = kwargs.pop('location', None)
        headers = kwargs.pop('headers', {})

        if location is not None:
            f = furl(request.url_root)
            f.path = location
            headers.update({
                'Location': '{0}'.format(f.url)
            })

        return super(Created, self).__init__(
            headers=headers,
            *args,
            **kwargs)


class NoContent(Response):
    """ Return a standard HTTP 204 Response. This should be used for returning
    responses to `DELETE` requests.

    Example
    -------
        >>> from fm import http
        >>> response = http.NoContent()

    """

    default_status = 204


class NotFound(Response):
    """ Returns a standard HTTP 404 Response. This should be used when a pgae
    foes not exist.

    Example
    -------
        >>> from fm import http
        >>> response = http.NotFound()

    """

    default_status = 404


class UnprocessableEntity(Response):
    """ Return a standard HTTP 422 Response. This should be used for raising
    validation errors back to the client.

    Example
    -------
        >>> from fm import http
        >>> response = http.UnprocessableEntity(errors=[{'foo': 'bar'}])

    """

    default_status = 422

    def __init__(self, *args, **kwargs):
        """ Overrides parent constructor allowing error messages to be passed
        into the response data.
        """

        errors = kwargs.pop('errors', [])
        message = kwargs.get('message', 'Validation Error')

        response = {
            'message': message,
            'errors': errors
        }

        return super(UnprocessableEntity, self).__init__(
            response,
            *args,
            **kwargs)
