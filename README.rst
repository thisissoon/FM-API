FM-API
======

Simple Flask API Interface to the physical FM Player via Redis Pub Sub.

Responses
---------

The API design is heavily influenced by GitHubs REST API design and this document
http://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api.

The API will only return response data where appropriate, for example a ``POST`` which
results in a new object being created will not result in the data of the created object
being returned, instead a ``Location`` header will be included in the response which will
be the link to the newly created resource.

When a response does include a response body this body will **always** be a JSON object.

This API does not prefix custom headers with the ``X-`` prefix as this is now deprecated:
https://tools.ietf.org/html/rfc6648.

Pagination
----------

For resources which support pagination response will return a JSON list of objects. Pagination
meta data will be returned in the response headers:

* ``Link``: Will contain a comma separated list of first, previous, next and last urls, see:
  http://tools.ietf.org/html/rfc5988#page-6 for more information.
* ``Total-Pages``: The total number of pages
* ``Total-Count``: The total number of items that are paginated

Example Response
~~~~~~~~~~~~~~~~

.. code-block::

    curl http://localhost/tracks\?limit\=1\&page\=4

    HTTP/1.0 200 OK
    Content-Length: 759
    Content-Type: application/json; charset=utf-8
    Date: Wed, 04 Mar 2015 11:35:24 GMT
    Link: <http://localhost/tracks?limit=1&page=1>; rel="first", <http://localhost/tracks?limit=1&page=3>; rel="prev", <http://localhost/tracks?limit=1&page=5>; rel="next", <http://localhost/tracks?limit=1&page=10>; rel="last"
    Server: Werkzeug/0.10.1 Python/2.7.3
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload
    Total-Count: 10
    Total-Pages: 10

    [
        ...
    ]

Resources
---------

``/player/playlist``
~~~~~~~~~~~~~~~~~~~~

``GET``
^^^^^^^

Returns the current playlist.

``POST``
^^^^^^^^

Append a track to the playlist.

``/player/pause``
~~~~~~~~~~~~~~~~~

``POST``
^^^^^^^^

Create a pause event, this will stop the playback.

``DELETE``
^^^^^^^^^^

Delete the pause event, this will resume the playback.
