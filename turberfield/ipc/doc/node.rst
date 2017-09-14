..  Titling
    ##++::==~~--''``

DIF Nodes
=========

Turberfield IPC can build for you a network node object, which takes your parcelled
messages and delivers them to others listening via the distributed IPC framework
(DIF).

Tokens
~~~~~~

You'll need a DIF token to use the framework. For now, the function
:py:func:`turberfield.ipc.fsdb.token` is the source of these.

Down and up
~~~~~~~~~~~

Turberfield's interface with the network point of attachment (POA) is via a pair of asyncio_
queues. The `down` queue takes your messages into the network, and the `up` queue is where
messages arrive from the network.

Mechanisms and policies
~~~~~~~~~~~~~~~~~~~~~~~

Inspired by John Day's `Patterns in Network Architecture`_, the design of
Turberfield IPC decouples network mechanisms and the policies which control
them. A node can adopt the policies it wishes. However, there is only a minimal
implementation (over UDP) at the moment, and so only one way of configuring a
node.

Creating a network node
~~~~~~~~~~~~~~~~~~~~~~~

The module provides a convenience function to build a network node with the
currently available routing functionality.

.. automodule:: turberfield.ipc.node

.. _patterns in network architecture: http://lccn.loc.gov/2007040174
.. _reliable transport connections: http://rina.tssg.org/docs/2009-014-reliable-conn-mgmt.pdf
