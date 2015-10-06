..  Titling
    ##++::==~~--''``

Example
=======


Windows
~~~~~~~

::

    start %HOME%\py3.5\scripts\python -m turberfield.ipc.demo.router

::

    start %HOME%\py3.5\scripts\python -m turberfield.ipc.demo.sender

::

    2015-10-06 15:43:42,243 INFO    turberfield.ipc.demo.sender|Sending message: Message(header=Header(id='57389f95fbf142c4869059306c3c0b3d', src=Address(namespace='turberfield', user='thustings', service='demo', application='turberfield.ipc.demo.sender'), dst=Address(namespace='turberfield', user='thustings', service='demo', application='turberfield.ipc.demo.sender'), hMax=3, via=Address(namespace='turberfield', user='thustings', service='demo', application='turberfield.ipc.demo.router'), hop=0), payload=(Alert(ts=datetime.datetime(2015, 10, 6, 15, 43, 42, 242283), text='Hello World!'),))
    2015-10-06 15:43:42,272 INFO    turberfield.ipc.demo.sender|Received: Message(header=Header(id='57389f95fbf142c4869059306c3c0b3d', src=Address(namespace='turberfield', user='thustings', service='demo', application='turberfield.ipc.demo.sender'), dst=Address(namespace='turberfield', user='thustings', service='demo', application='turberfield.ipc.demo.sender'), hMax=3, via=Address(namespace='turberfield', user='thustings', service='demo', application='turberfield.ipc.demo.sender'), hop=3), payload=[Alert(ts=datetime.datetime(2015, 10, 6, 15, 43, 42), text='Hello World!')])
