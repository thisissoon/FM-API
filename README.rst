FM-API
======

Simple Flask API Interface to the physical FM Player via Redis Pub Sub.

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
