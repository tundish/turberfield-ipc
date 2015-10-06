..  Titling
    ##++::==~~--''``

Messages
========

The :py:mod:`message <turberfield.ipc.message>` module takes the objects
used by your application and parcels them up for transmission. The message
it creates contains a header with routing and flow control information.

The syntax of messages is RSON_, which is a variant of JSON with some extra
features.

The module provides a mechanism by which you can register your application classes for
serialisation over the network.


.. automodule:: turberfield.ipc.message

.. autofunction:: turberfield.ipc.message.dumps

.. autofunction:: turberfield.ipc.message.load

.. autofunction:: turberfield.ipc.message.replace

.. autofunction:: turberfield.ipc.message.parcel

.. _RSON: https://code.google.com/p/rson/wiki/Manual
