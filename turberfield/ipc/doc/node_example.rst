..  Titling
    ##++::==~~--''``

DIF Example
===========

A common demonstration of a networked application is `echo server/ echo
client`. The action of looping back the message is usually hardcoded in the
server.

In a distributed network, loopback is a routing function, not an
application behaviour. All Turberfield IPC network nodes perform routing.

A message routing demo
~~~~~~~~~~~~~~~~~~~~~~

The package `turberfield.ipc.demo` contains two modules, `router` and `sender`.
These are defined separately for convenience. If you look at the code you'll
see they do the same thing; they call
:py:func:`turberfield.ipc.node.create_udp_node`. The `sender` module in
addition creates a message and places it into its `down` queue.

The entire demo is achieved in only a few lines of code::

    def main(args):
        .
        .
        .

        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)

        down = asyncio.Queue(loop=loop)
        up = asyncio.Queue(loop=loop)

        tok = token(args.connect, APP_NAME)
        node = create_udp_node(loop, tok, down, up)
        loop.create_task(node(token=tok))

        msg = parcel(
            tok,
            Alert(datetime.datetime.now(), "Hello World!"),
            via=Address(tok.namespace, tok.user, tok.service, turberfield.ipc.demo.router.APP_NAME)
        )
        loop.call_soon_threadsafe(functools.partial(down.put_nowait, msg))
        loop.run_forever()

Run on Windows
~~~~~~~~~~~~~~

Install `turberfield-ipc` into a Python virtual environment at `%HOME%\\py3.5`.

Open up a console and start the `router` process::

    start %HOME%\py3.5\scripts\python -m turberfield.ipc.demo.router

Then after that has launched, do the same with the `sender` process::

    start %HOME%\py3.5\scripts\python -m turberfield.ipc.demo.sender

Run on Linux
~~~~~~~~~~~~

Install `turberfield-ipc` into a Python virtual environment at `~/py3.5`.

Open up a console and start the `router` process::

    ~/py3.5/bin/python -m turberfield.ipc.demo.router &

Then after that has launched, do the same with the `sender` process::

    ~/py3.5/bin/python -m turberfield.ipc.demo.sender &

Output
~~~~~~

The captured log is shown below, with some re-tabulation for clarity.
Here is the initial message from `sender`. Note how the hop number is initially 0.::

    2015-10-06 15:43:42,243 INFO    turberfield.ipc.demo.sender|Sending message:
        Message(header=Header(id='57389f95fbf142c4869059306c3c0b3d',
        src=Address(namespace='turberfield', user='alice', service='demo', application='turberfield.ipc.demo.sender'),
        dst=Address(namespace='turberfield', user='alice', service='demo', application='turberfield.ipc.demo.sender'),
        hMax=3,
        via=Address(namespace='turberfield', user='alice', service='demo', application='turberfield.ipc.demo.router'),
        hop=0),
        payload=(Alert(ts=datetime.datetime(2015, 10, 6, 15, 43, 42, 242283), text='Hello World!'),))

Here is the message after it has reached the router, gone back to the sender and emerged
from the node. The hop number is now 3 (one hop from the sender node onto the network POA,
one hop back from the router, and another to come out of the node again)::

    2015-10-06 15:43:42,272 INFO    turberfield.ipc.demo.sender|Received:
        Message(header=Header(id='57389f95fbf142c4869059306c3c0b3d',
        src=Address(namespace='turberfield', user='alice', service='demo', application='turberfield.ipc.demo.sender'),
        dst=Address(namespace='turberfield', user='alice', service='demo', application='turberfield.ipc.demo.sender'),
        hMax=3,
        via=Address(namespace='turberfield', user='alice', service='demo', application='turberfield.ipc.demo.sender'),
        hop=3),
        payload=[Alert(ts=datetime.datetime(2015, 10, 6, 15, 43, 42), text='Hello World!')])
