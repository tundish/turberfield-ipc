..  Titling
    ##++::==~~--''``

.. _proactor:

Proactor
========

The :py:mod:`proactor <turberfield.ipc.proactor>` module
establishes a pattern for inter-process communication using two standard
technologies:

    * Configuration of processes from a `configparser`-compatible file.
    * Message passing via RESTful web-hooks over an http transport.

.. automodule:: turberfield.ipc.proactor

Base class
~~~~~~~~~~

.. autoclass:: turberfield.ipc.proactor.Proactor
   :members:

Initiator
~~~~~~~~~

.. autoclass:: turberfield.ipc.proactor.Initiator
   :members: next_port, launch

Data structures
~~~~~~~~~~~~~~~

.. autoattribute:: turberfield.ipc.proactor.Initiator.Worker
   :annotation: (guid, port, session, module, process). The details for
        a worker process:

        guid
            A unique id which identifies a section in the configuration file.
        port
            The port the worker process is listening on.
        session
            An optional value for the job which may be of use in web applications.
        module
            The executable Python module used to launch the job.
        process
            A reference to the Python subprocess.
