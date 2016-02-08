..  Titling
    ##++::==~~--''``

Messages
========

Turberfield IPC can take the objects used by your application and parcel them up for
transmission. The messages get passed around with a header of routing and flow control
information.

You'll need to register your application classes for encapsulation in these messages.


Defined types
~~~~~~~~~~~~~

.. autoclass:: turberfield.ipc.types.Address

.. autoclass:: turberfield.ipc.message.Message


Creating messages
~~~~~~~~~~~~~~~~~

.. autofunction:: turberfield.ipc.message.parcel

Replying to messages
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: turberfield.ipc.message.reply

Registering custom objects
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: turberfield.ipc.message

Other functions
~~~~~~~~~~~~~~~

.. autofunction:: turberfield.ipc.fsdb.token

