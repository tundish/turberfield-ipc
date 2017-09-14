..  Titling
    ##++::==~~--''``

Proactor Example
================

Two files in the *demo* directory show how to create **processor** and **initiator**
modules. There is also a configuration file for them.

Configuration file
~~~~~~~~~~~~~~~~~~

The file `demo/proactor.cfg` has four sections.

    #. A `DEFAULT` section with global default settings.
    #. A `turberfield.ipc.demo.initiator` section with defaults for initiator processes.
    #. A `turberfield.ipc.demo.processor` section with defaults for processors. In this
       example it  is empty.
    #. A section named with a global id value (line 14). This section contains settings
       for a specific process. Notice how it references the values in the
       `turberfield.ipc.demo.initiator` section.

.. include:: ../demo/proactor.cfg
   :code: ini
   :number-lines: 1

Run on Linux
~~~~~~~~~~~~

Install `turberfield-ipc` into a Python virtual environment at `~/py3.5`.

Open up a console and start the `initiator` process::

    ~/py3.5/bin/python -m turberfield.ipc.demo.initiator \
    --guid=8d740c16d9b8419aa7417f7da6deb039 \
    --config=turberfield/ipc/demo/proactor.cfg

This command will run an initiator process, feed into it the configuration file
and tell it to get its settings from the specific section named by the guid::

    2017-09-14 18:04:16,425 INFO   |1034|turberfield|Place defaults
    2017-09-14 18:04:16,426 INFO   |1034|turberfield|Read config...
    2017-09-14 18:04:16,426 INFO   |1034|turberfield.ipc.proactor.initiator|Running jobs
    2017-09-14 18:04:16,428 INFO   |1034|turberfield|Serving on 0.0.0.0:8080

Launch a worker
~~~~~~~~~~~~~~~

The demo initiator has a web API endpoint which lets you create workers. You can operate
it from the command line like this::

    curl -X POST localhost:8080/create
    201: Created

You'll see a new processor start up and begin logging messages::

    2017-09-14 18:11:30,302 INFO   |1065|turberfield.processor|Read config...
    2017-09-14 18:11:30,306 INFO   |1065|turberfield.processor|Serving on 0.0.0.0:49152

Reconfiguration of a live processor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The initiator endpoint at ``localhost:8080/config/`` allows a processor to request its
configuration. The processor must use its *guid* as the last part of the url, and authenticate
itself with a secret token that it gets from its most recent configuration.

Every 30 seconds or so you will see the processor request a fresh configuration from the
initiator. This demo simply logs that data. A more sophisticated application would update
its configuration. That configuration might well include a refresh of the authentication token.

Message passing
~~~~~~~~~~~~~~~

The initiator can publish endpoints to its processors, and authenticate the tokens
they use in their requests.

Alternatively, processors could respond to API requests whether from the initiator
or from each other. All sorts of messaging sequences are now possible.

This flexible system can form the basis of an asynchronous distributed computational
service controlled by the initiator.
