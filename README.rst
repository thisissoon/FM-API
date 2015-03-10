FM-API
======

Simple Flask API Interface to the physical FM Player via Redis Pub Sub.

All examples use ``HTTPie`` - http://httpie.org

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

Example
~~~~~~~

.. code-block::

    http GET http://localhost/tracks\?limit\=1\&page\=4

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

Validation
----------

In the event of validation errors the API will response with a ``422 - Unprocessable Entity``. The
response data will contain a JSON object detailing the errors.

Example
~~~~~~~

.. code-block::

    http POST http://localhost/player/queue uri=spotify:track:

    HTTP/1.0 422 UNPROCESSABLE ENTITY
    Content-Length: 97
    Content-Type: application/json; charset=utf-8
    Date: Wed, 04 Mar 2015 14:55:34 GMT
    Server: Werkzeug/0.10.1 Python/2.7.3
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload

    {
        "errors": {
            "uri": [
                "Invalid Spotify Track URI: spotify:track:",
                "Another Error"
            ]
        },
        "message": "Validation Error"
    }


Events
------

The API will publish several events to a Redis Pubsub channel called ``fm:events``. This events
include pause events and track adding. All events sent by the system are sent as JSON objects with an
element in the object called ``event`` with the value being the event type.

Pause
~~~~~

The pause event is published from the ``/player/pause`` resource.

.. code-block::

    {
        'event': 'pause'
    }

Resume
~~~~~~

The pause event is published from the ``/player/resume`` resource.

.. code-block::

    {
        'event': 'resume'
    }

Add
~~~

The add event is published from the ``/player/queue`` resource on successful ``POST`` requests which
indicates a new track has been added to the queue. This event will also include a ``uri`` element
containing the Spotify URI.

.. code-block::

    {
        'event': 'add',
        'uri' 'spotify:track:3Esqxo3D31RCjmdgwBPbOO'
    }

Play
~~~~

This event is fired by the physical player to indicate when track playback begins. This will also contain
a ``uri`` element containing the Spotify URI.

.. code-block::

    {
        'event': 'plau',
        'uri' 'spotify:track:3Esqxo3D31RCjmdgwBPbOO'
    }

End
~~~

This event is fired by the physical player to indicate when track playback ends. This will also contain
a ``uri`` element containing the Spotify URI.

.. code-block::

    {
        'event': 'end',
        'uri' 'spotify:track:3Esqxo3D31RCjmdgwBPbOO'
    }

Resources
---------

``/player/queue``
~~~~~~~~~~~~~~~~~~~~

Manages the current playlist queue - does not include the current playing track.

``GET``
^^^^^^^

Returns the current paginated playlist. This resource will return a JSON list of Track objects, including
album and artist nested objects.

.. code-block::

    http GET http://localhost/player/queue\?limit\=5

    HTTP/1.0 200 OK
    Content-Length: 3811
    Content-Type: application/json; charset=utf-8
    Date: Wed, 04 Mar 2015 13:58:09 GMT
    Link: <http://localhost/player/queue?limit=5&page=2>; rel="next", <http://localhost/player/queue?limit=5&page=4>; rel="last"
    Server: Werkzeug/0.10.1 Python/2.7.3
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload
    Total-Count: 17
    Total-Pages: 4

    [
        {
            "album": {
                "artists": [
                    {
                        "id": "26556f7e-3304-4e51-8243-dd2199fcf6fa",
                        "name": "Nightwish",
                        "spotify_uri": "spotify:artist:2NPduAUeLVsfIauhRwuft1"
                    }
                ],
                "id": "7f8bda77-5364-4902-9a98-208f1cdd7643",
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/7928fc9bd902b917aae0ef1bee41cb51598a2d27",
                        "width": 640
                    },
                    {
                        "height": 300,
                        "url": "https://i.scdn.co/image/e80cb4d324d16881e2f7653abdbd70497bbab68d",
                        "width": 300
                    },
                    {
                        "height": 64,
                        "url": "https://i.scdn.co/image/bf567406035a8e2b162c6a23470c6cdd5dd560f3",
                        "width": 64
                    }
                ],
                "name": "Showtime, Storytime",
                "spotify_uri": "spotify:album:1tZlCjdI2dcfBXP8iSDsSI"
            },
            "duration": 272906,
            "id": "4b170737-017c-4e85-965c-47b8a158c789",
            "name": "Dark Chest Of Wonders - Live @ Wacken 2013",
            "spotify_uri": "spotify:track:6FshvOVICpRVkwpYE5BYTD"
        },
        ...
    ]


``POST``
^^^^^^^^

Add a track to the playlist. This resource does not return an data. The ``Location`` Header can
used to then request the track object.

.. code-block::

    http POST http://localhost/player/queue uri=spotify:track:6cBnzMuhvD0911UfSkNHIN

    HTTP/1.0 201 CREATED
    Content-Length: 0
    Content-Type: application/json; charset=utf-8
    Date: Wed, 04 Mar 2015 13:53:52 GMT
    Location: http://localhost/tracks/track/c3111ce3-ef00-4bc3-b9ff-22979fe305e7
    Server: Werkzeug/0.10.1 Python/2.7.3
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload


``/player/current``
~~~~~~~~~~~~~~~~~~~

This resource interacts with the currently playing track.

``GET``
^^^^^^^

Returns the currently playing track. In the event a track is not playing a ``204 No Content`` will be returned.
Also a ``Paused`` header is included in the response, this is to ensure the correct state of the playing track
is observed, in the event the track is paused the value will be ``1`` else it will be ``0``.

.. code-block::

    http GET http://$DOCKER_IP:5000/player/current

    HTTP/1.0 200 OK
    Content-Length: 1542
    Content-Type: application/json; charset=utf-8
    Date: Wed, 04 Mar 2015 14:27:39 GMT
    Paused: 0
    Server: Werkzeug/0.10.1 Python/2.7.3
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload

    {
        "album": {
            "artists": [
                {
                    "id": "26556f7e-3304-4e51-8243-dd2199fcf6fa",
                    "name": "Nightwish",
                    "spotify_uri": "spotify:artist:2NPduAUeLVsfIauhRwuft1"
                }
            ],
            "id": "7f8bda77-5364-4902-9a98-208f1cdd7643",
            "images": [
                {
                    "height": 640,
                    "url": "https://i.scdn.co/image/7928fc9bd902b917aae0ef1bee41cb51598a2d27",
                    "width": 640
                },
                {
                    "height": 300,
                    "url": "https://i.scdn.co/image/e80cb4d324d16881e2f7653abdbd70497bbab68d",
                    "width": 300
                },
                {
                    "height": 64,
                    "url": "https://i.scdn.co/image/bf567406035a8e2b162c6a23470c6cdd5dd560f3",
                    "width": 64
                }
            ],
            "name": "Showtime, Storytime",
            "spotify_uri": "spotify:album:1tZlCjdI2dcfBXP8iSDsSI"
        },
        "duration": 272906,
        "id": "4b170737-017c-4e85-965c-47b8a158c789",
        "name": "Dark Chest Of Wonders - Live @ Wacken 2013",
        "spotify_uri": "spotify:track:6FshvOVICpRVkwpYE5BYTD"
    }

``/player/pause``
~~~~~~~~~~~~~~~~~

This resource manages the pausing of the playback and acts as a creatable and deletable object.

``POST``
^^^^^^^^

Create a pause event, this will stop the playback.

.. code-block::

    http POST http://localhost/player/pause

    HTTP/1.0 201 CREATED
    Content-Length: 0
    Content-Type: application/json; charset=utf-8
    Date: Wed, 04 Mar 2015 14:04:54 GMT
    Server: Werkzeug/0.10.1 Python/2.7.3
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload

``DELETE``
^^^^^^^^^^

Delete the pause event, this will resume the playback.

.. code-block::

    http DELETE http://localhost/player/pause

    HTTP/1.0 204 NO CONTENT
    Content-Length: 0
    Content-Type: application/json; charset=utf-8
    Date: Wed, 04 Mar 2015 14:04:54 GMT
    Server: Werkzeug/0.10.1 Python/2.7.3
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload


``/tracks``
~~~~~~~~~~~

This resource operates on the tracks currently stored in the local database.

``GET``
^^^^^^^

Returns a paginated list of tracks in no particular order.

.. code-block::

    http GET http://$DOCKER_IP:5000/tracks\?limit\=2

    HTTP/1.0 200 OK
    Content-Length: 1542
    Content-Type: application/json; charset=utf-8
    Date: Wed, 04 Mar 2015 14:27:39 GMT
    Link: <http://localhost/tracks?limit=2&page=2>; rel="next", <http://localhost/tracks?limit=2&page=5>; rel="last"
    Server: Werkzeug/0.10.1 Python/2.7.3
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload
    Total-Count: 10
    Total-Pages: 5

    [
        {
            "album": {
                "artists": [
                    {
                        "id": "26556f7e-3304-4e51-8243-dd2199fcf6fa",
                        "name": "Nightwish",
                        "spotify_uri": "spotify:artist:2NPduAUeLVsfIauhRwuft1"
                    }
                ],
                "id": "7f8bda77-5364-4902-9a98-208f1cdd7643",
                "images": [
                    {
                        "height": 640,
                        "url": "https://i.scdn.co/image/7928fc9bd902b917aae0ef1bee41cb51598a2d27",
                        "width": 640
                    },
                    {
                        "height": 300,
                        "url": "https://i.scdn.co/image/e80cb4d324d16881e2f7653abdbd70497bbab68d",
                        "width": 300
                    },
                    {
                        "height": 64,
                        "url": "https://i.scdn.co/image/bf567406035a8e2b162c6a23470c6cdd5dd560f3",
                        "width": 64
                    }
                ],
                "name": "Showtime, Storytime",
                "spotify_uri": "spotify:album:1tZlCjdI2dcfBXP8iSDsSI"
            },
            "duration": 272906,
            "id": "4b170737-017c-4e85-965c-47b8a158c789",
            "name": "Dark Chest Of Wonders - Live @ Wacken 2013",
            "spotify_uri": "spotify:track:6FshvOVICpRVkwpYE5BYTD"
        },
        ...
    ]

``/tracks/<id>``
~~~~~~~~~~~~~~~~~~~~~~

This resource operates on specific tracks in the local database.

``GET``
^^^^^^^

Returns the specific track object.

.. code-block::

    http GET http://localhost/tracks/4b170737-017c-4e85-965c-47b8a158c789

    HTTP/1.0 200 OK
    Content-Length: 1542
    Content-Type: application/json; charset=utf-8
    Date: Wed, 04 Mar 2015 14:27:39 GMT
    Server: Werkzeug/0.10.1 Python/2.7.3
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload

    {
        "album": {
            "artists": [
                {
                    "id": "26556f7e-3304-4e51-8243-dd2199fcf6fa",
                    "name": "Nightwish",
                    "spotify_uri": "spotify:artist:2NPduAUeLVsfIauhRwuft1"
                }
            ],
            "id": "7f8bda77-5364-4902-9a98-208f1cdd7643",
            "images": [
                {
                    "height": 640,
                    "url": "https://i.scdn.co/image/7928fc9bd902b917aae0ef1bee41cb51598a2d27",
                    "width": 640
                },
                {
                    "height": 300,
                    "url": "https://i.scdn.co/image/e80cb4d324d16881e2f7653abdbd70497bbab68d",
                    "width": 300
                },
                {
                    "height": 64,
                    "url": "https://i.scdn.co/image/bf567406035a8e2b162c6a23470c6cdd5dd560f3",
                    "width": 64
                }
            ],
            "name": "Showtime, Storytime",
            "spotify_uri": "spotify:album:1tZlCjdI2dcfBXP8iSDsSI"
        },
        "duration": 272906,
        "id": "4b170737-017c-4e85-965c-47b8a158c789",
        "name": "Dark Chest Of Wonders - Live @ Wacken 2013",
        "spotify_uri": "spotify:track:6FshvOVICpRVkwpYE5BYTD"
    }
