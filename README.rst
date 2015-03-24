FM-API
======

|circle| |coveralls|

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


Volume Changed
~~~~~~~~~~~~~~

Fired by the player when the volume onn the player has been changed. Contains a volume attribute with
the volume level number between 0 and 100.

.. code-block::

    {
        'event': 'volume_changed',
        'volume' 50
    }

Mute Changed
~~~~~~~~~~~~

Fired when the mute state changes on the player. Contains a mute attribute with the mute state as a
boolean.

.. code-block::

    {
        'event': 'mute_changed',
        'mute' True
    }

Authentication
--------------

Authentication is handled via the Google+ OAuth2 Web Flow. The accounts are limited to those defined in
configuration (``thisissoon.com`` and ``thishe.re``). Login should be performed on initial page load using
the Google+ OAuth2 web flow, this should pass an authentication token to the ``/oauth2/google/connect``
resource.

Example Request
~~~~~~~~~~~~~~~

.. code-block::

    GET /oauth2/google/conenct HTTP/1.1
    Accept: application/json
    Accept-Encoding: gzip, deflate
    Connection: keep-alive
    Host: 192.168.59.103:5000

    {
        "code": "123456abcde"
    }

The API will validate the token and return an ``Access-Token`` header to be used for subsequent requests. These
tokens do not currently expire.

Example Response
~~~~~~~~~~~~~~~~

If a new user is created in the system the response will be a standard ``201`` else the response will be a ``200``.

.. code-block::

    HTTP/1.0 201 OK
    Access-Control-Allow-Credentials: true
    Access-Control-Allow-Expose-Headers: Link, Total-Pages, Total-Count, Access-Token
    Access-Control-Allow-Origin: *
    Access-Token: 12234fn1uu21euid1nu23f3jn2f
    Content-Length: 5301
    Content-Type: application/json; charset=utf-8
    Date: Mon, 09 Mar 2015 08:01:33 GMT
    Location: http://192.168.59.103:5000/users/1234-abcde-1421-bfhdsk
    Server: Werkzeug/0.10.1 Python/2.7.3
    Status: 201 Created
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload

Once a valid ``Access-Token`` has been retrieved this can be used for each subsequent request to protected
resources. This can be stored in a cookie for example and could bypass the need for Google+ OAuth2 login.

Resources
---------

``/oauth2/google/connect``
~~~~~~~~~~~~~~~~~~~~~~~~~~

This resource handles authentication using Google+ OAuth2 Web Flow tokens.

``POST``
^^^^^^^^

Call this resource with a ``POST`` method to authenticate a user. This resource will return a ``200``
for existing users and a ``201`` for newly created users. The request body should contain a JSON object
which contains the OAuth2 token returned by the OAuth2 webflow.

On a successful response an ``Access-Token`` header will be returned which can be used to authenticate
each subsequent request to protected resources.

Example Request
***************

.. code-block::

    POST /oauth2/google/connect HTTP/1.1
    Accept: application/json
    Accept-Encoding: gzip, deflate
    Access-Token: abcde1234
    Connection: keep-alive
    Content-Length: 0
    Content-Type: application/json; charset=utf-8
    Host: localhost
    User-Agent: HTTPie/0.8.0

    {
        token: "google-oauth2-token"
    }

Example Response
****************

.. code-block::

    Access-Control-Allow-Credentials: true
    Access-Control-Allow-Expose-Headers: Link, Total-Pages, Total-Count, Access-Token
    Access-Control-Allow-Origin: *
    Cache-Control: no-cache, no-store, must-revalidate
    Content-Length: 21
    Content-Type: application/json; charset=utf-8
    Date: Thu, 19 Mar 2015 12:11:24 GMT
    Expires: 0
    Pragma: no-cache
    Server: Werkzeug/0.10.1 Python/2.7.3
    Status: 200 OK
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload

    {
        access_token: "IjgyNThiZTZiLWVlNTMtNDE4Ni04YmJkLTU1YmMwYTNhNmYyNCI.B-xObA.dvEM7STtNIJhgrQdfBmGwBrVV-Q"
    }

``/oauth2/google/client``
~~~~~~~~~~~~~~~~~~~~~~~~~

**Note**: Only available when in ``DEBUG`` mode

This page can be accessed in your web browser and is an OAuth2 Test Client.

``/player/queue``
~~~~~~~~~~~~~~~~~

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
                "uri": "spotify:album:1tZlCjdI2dcfBXP8iSDsSI"
            },
            "artists": [
                {
                    "id": "26556f7e-3304-4e51-8243-dd2199fcf6fa",
                    "name": "Nightwish",
                    "uri": "spotify:artist:2NPduAUeLVsfIauhRwuft1"
                }
            ],
            "duration": 272906,
            "id": "4b170737-017c-4e85-965c-47b8a158c789",
            "name": "Dark Chest Of Wonders - Live @ Wacken 2013",
            "uri": "spotify:track:6FshvOVICpRVkwpYE5BYTD"
        },
        ...
    ]


``POST``
^^^^^^^^

**Note**: Requires valid ``Access-Token``

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
            "uri": "spotify:album:1tZlCjdI2dcfBXP8iSDsSI"
        },
        "artists": [
            {
                "id": "26556f7e-3304-4e51-8243-dd2199fcf6fa",
                "name": "Nightwish",
                "uri": "spotify:artist:2NPduAUeLVsfIauhRwuft1"
            }
        ],
        "duration": 272906,
        "id": "4b170737-017c-4e85-965c-47b8a158c789",
        "name": "Dark Chest Of Wonders - Live @ Wacken 2013",
        "uri": "spotify:track:6FshvOVICpRVkwpYE5BYTD"
    }


``DELETE``
^^^^^^^^^^

**Note**: Requires valid ``Access-Token``

Issuing a ``DELETE`` to the current track resource will result in the track being skipped and the
next track in the queue being played. This resource will always return a ``204``.

.. code-block::

    http -jv DELETE http://localhost/player/current

    DELETE /player/current HTTP/1.1
    Accept: application/json
    Accept-Encoding: gzip, deflate
    Access-Token: abcde1234
    Connection: keep-alive
    Content-Length: 0
    Content-Type: application/json; charset=utf-8
    Host: 192.168.59.103:5000
    User-Agent: HTTPie/0.8.0

    HTTP/1.0 204 NO CONTENT
    Access-Control-Allow-Credentials: true
    Access-Control-Allow-Expose-Headers: Link, Total-Pages, Total-Count
    Access-Control-Allow-Origin: *
    Cache-Control: no-cache, no-store, must-revalidate
    Content-Length: 0
    Content-Type: application/json; charset=utf-8
    Date: Wed, 18 Mar 2015 13:24:29 GMT
    Expires: 0
    Pragma: no-cache
    Server: Werkzeug/0.10.1 Python/2.7.3
    Status: 204 No Content
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload


``/player/pause``
~~~~~~~~~~~~~~~~~

This resource manages the pausing of the playback and acts as a creatable and deletable object.

``POST``
^^^^^^^^

**Note**: Requires valid ``Access-Token``

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

**Note**: Requires valid ``Access-Token``

Delete the pause event, this will resume the playback.

.. code-block::

    http DELETE http://localhost/player/pause

    HTTP/1.0 204 NO CONTENT
    Content-Length: 0
    Content-Type: application/json; charset=utf-8
    Date: Wed, 04 Mar 2015 14:04:54 GMT
    Server: Werkzeug/0.10.1 Python/2.7.3
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload


``/player/volume``
~~~~~~~~~~~~~~~~~~

Managed the volume on the physical player.

``GET``
^^^^^^^

Returns the current volume level of the player.

.. code-block::

    http GET http://localhost/player/volume

    HTTP/1.0 200 OK
    Content-Length: 1542
    Content-Type: application/json; charset=utf-8
    Date: Wed, 04 Mar 2015 14:27:39 GMT
    Paused: 0
    Server: Werkzeug/0.10.1 Python/2.7.3
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload

    {
        "volume": 50
    }

``POST``
^^^^^^^^

**Note**: Requires valid ``Access-Token``

Allows the ability to change the volume. The post data must be a number betweeb 0 and 100 else
a validation error will be returned.

.. code-block::

    http -jv POST http://localhost/player/volume

    POST /player/volume HTTP/1.1
    Accept: application/json
    Accept-Encoding: gzip, deflate
    Connection: keep-alive
    Content-Length: 14
    Content-Type: application/json; charset=utf-8
    Host: 192.168.59.103:5000
    User-Agent: HTTPie/0.8.0

    {
        "volume": 80
    }

    HTTP/1.0 200 OK
    Access-Control-Allow-Credentials: true
    Access-Control-Allow-Expose-Headers: Link, Total-Pages, Total-Count
    Access-Control-Allow-Origin: *
    Content-Length: 0
    Content-Type: application/json; charset=utf-8
    Date: Wed, 11 Mar 2015 12:16:45 GMT
    Server: Werkzeug/0.10.1 Python/2.7.3
    Status: 200 OK
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload

``/player/mute``
~~~~~~~~~~~~~~~~

This resource manages the mute state of the player and followa the same convention as the ``/player/pause``
resource.

``GET``
^^^^^^^

Returns the current mute state.

.. code-block::

    http GET http://localhost/player/mute

    HTTP/1.0 200 OK
    Content-Length: 1542
    Content-Type: application/json; charset=utf-8
    Date: Wed, 04 Mar 2015 14:27:39 GMT
    Paused: 0
    Server: Werkzeug/0.10.1 Python/2.7.3
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload

    {
        "mute": true
    }

``POST``
^^^^^^^^

**Note**: Requires valid ``Access-Token``

Sets the player mute state to ``True``.

.. code-block::

    http -jv POST http://localhost/player/mute

    POST /player/mute HTTP/1.1
    Accept: application/json
    Accept-Encoding: gzip, deflate
    Connection: keep-alive
    Content-Length: 0
    Content-Type: application/json; charset=utf-8
    Host: 192.168.59.103:5000
    User-Agent: HTTPie/0.8.0

    HTTP/1.0 201 CREATED
    Access-Control-Allow-Credentials: true
    Access-Control-Allow-Expose-Headers: Link, Total-Pages, Total-Count
    Access-Control-Allow-Origin: *
    Content-Length: 0
    Content-Type: application/json; charset=utf-8
    Date: Wed, 11 Mar 2015 12:20:10 GMT
    Server: Werkzeug/0.10.1 Python/2.7.3
    Status: 201 Created
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload

``DELETE``
^^^^^^^^^^

**Note**: Requires valid ``Access-Token``

Sets the player mute state to ``False``.

.. code-block::

    http -jv DELETE http://localhost/player/mute

    DELETE /player/mute HTTP/1.1
    Accept: application/json
    Accept-Encoding: gzip, deflate
    Connection: keep-alive
    Content-Length: 0
    Content-Type: application/json; charset=utf-8
    Host: 192.168.59.103:5000
    User-Agent: HTTPie/0.8.0

    HTTP/1.0 204 NO CONTENT
    Access-Control-Allow-Credentials: true
    Access-Control-Allow-Expose-Headers: Link, Total-Pages, Total-Count
    Access-Control-Allow-Origin: *
    Content-Length: 0
    Content-Type: application/json; charset=utf-8
    Date: Wed, 11 Mar 2015 12:21:37 GMT
    Server: Werkzeug/0.10.1 Python/2.7.3
    Status: 204 No Content
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
                "uri": "spotify:album:1tZlCjdI2dcfBXP8iSDsSI"
            },
            "artists": [
                {
                    "id": "26556f7e-3304-4e51-8243-dd2199fcf6fa",
                    "name": "Nightwish",
                    "uri": "spotify:artist:2NPduAUeLVsfIauhRwuft1"
                }
            ],
            "duration": 272906,
            "id": "4b170737-017c-4e85-965c-47b8a158c789",
            "name": "Dark Chest Of Wonders - Live @ Wacken 2013",
            "uri": "spotify:track:6FshvOVICpRVkwpYE5BYTD"
        },
        ...
    ]

``/tracks/<id_or_uri>``
~~~~~~~~~~~~~~~~~~~~~~

This resource operates on specific tracks in the local database. You can pass in a valid primary key
or Spotify URI to get the track data.

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
            "uri": "spotify:album:1tZlCjdI2dcfBXP8iSDsSI"
        },
        "artists": [
            {
                "id": "26556f7e-3304-4e51-8243-dd2199fcf6fa",
                "name": "Nightwish",
                "uri": "spotify:artist:2NPduAUeLVsfIauhRwuft1"
            }
        ],
        "duration": 272906,
        "id": "4b170737-017c-4e85-965c-47b8a158c789",
        "name": "Dark Chest Of Wonders - Live @ Wacken 2013",
        "uri": "spotify:track:6FshvOVICpRVkwpYE5BYTD"
    }

``/users/authenticated``
~~~~~~~~~~~~~~~~~~~~~~~~

This resource handles the current user.

``GET``
^^^^^^^

This will return the currently authenitcated user (``200``) else a ``401`` will be returned.

Example Request
***************

.. code-block::

    GET /users/authenticated HTTP/1.1
    Accept: */*
    Accept-Encoding: gzip, deflate
    Access-Token: IjgyNThiZTZiLWVlNTMtNDE4Ni04YmJkLTU1YmMwYTNhNmYyNCI.B-xObA.dvEM7STtNIJhgrQdfBmGwBrVV-Q
    Connection: keep-alive
    Host: localhost
    User-Agent: HTTPie/0.8.0

Example Response
****************

.. code-block::

    HTTP/1.0 200 OK
    Access-Control-Allow-Credentials: true
    Access-Control-Allow-Expose-Headers: Link, Total-Pages, Total-Count, Access-Token
    Access-Control-Allow-Origin: *
    Cache-Control: no-cache, no-store, must-revalidate
    Content-Length: 236
    Content-Type: application/json; charset=utf-8
    Date: Thu, 19 Mar 2015 12:46:45 GMT
    Expires: 0
    Pragma: no-cache
    Server: Werkzeug/0.10.1 Python/2.7.3
    Status: 200 OK
    Strict-Transport-Security: max-age=31536000; includeSubdomains; preload

    {
        "avatar_url": "https://lh5.googleusercontent.com/-8zjhd-e4yZA/AAAAAAAAAAI/AAAAAAAAAFU/NiS1oH4gAKo/photo.jpg",
        "display_name": "Chris Reeves",
        "family_name": "Reeves",
        "given_name": "Chris",
        "id": "8258be6b-ee53-4186-8bbd-55bc0a3a6f24"
    }

.. |circle| image:: https://img.shields.io/circleci/project/thisissoon/FM-API/master.svg?style=flat
    :target: https://circleci.com/gh/thisissoon/FM-API/tree/master

.. |coveralls| image:: https://img.shields.io/coveralls/thisissoon/FM-API/master.svg?style=flat
  :target: https://coveralls.io/r/thisissoon/FM-API?branch=master
