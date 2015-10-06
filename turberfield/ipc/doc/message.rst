..  Titling
    ##++::==~~--''``

Messages
========

Turberfield IPC can take the objects used by your application and parcel them up for
transmission. The messages get passed around with a header of routing and flow control
information.

The format of messages on the wire is UTF-8 encoded RSON_, which is a variant of JSON
with some extra features.

The :py:mod:`message <turberfield.ipc.message>` module provides a mechanism by which you
can register your own application classes for encapsulation in these messages.


Defined types
~~~~~~~~~~~~~

.. autoclass:: turberfield.ipc.types.Address

.. autoclass:: turberfield.ipc.message.Message


Creating messages
~~~~~~~~~~~~~~~~~

.. autofunction:: turberfield.ipc.message.parcel

Loading messages
~~~~~~~~~~~~~~~~

.. autofunction:: turberfield.ipc.message.loads

Registering custom objects
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: turberfield.ipc.message

Other functions
~~~~~~~~~~~~~~~

.. autofunction:: turberfield.ipc.fsdb.token

.. autofunction:: turberfield.ipc.message.dumps

.. autofunction:: turberfield.ipc.message.load

.. autofunction:: turberfield.ipc.message.replace

.. _RSON: https://code.google.com/p/rson/wiki/Manual
