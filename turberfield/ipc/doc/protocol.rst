..  Titling
    ##++::==~~--''``

Protocol
========

Point Of Attachment
===================

An agent which runs on behalf of the user with only their permissions.
Well-known local directory (.turberfield) replaces well-known ports for services.

Library functions to retrieve contact endpoint details.


Operations
==========

Enrolment
~~~~~~~~~

App (IPC client) joins DIF.
Establishes a flow (transient connection).

* Formation: Non-DIF contacts non-DIF; they form a DIF
* Invitation: DIF contacts non-DIF; they join the DIF
* Non-DIF contacts in-DIF; joins DIF ??? What is application Use Case?
* In-DIF contacts in-DIF; one more flow created (one more route?)

Encode as JSON.

* Fixed-length header gives lengths of content
* Check field typing.

cf: CDAP_

Synchronisation
~~~~~~~~~~~~~~~

* Select Policy (UDP/subprocess)
* Allocate port on request
* Agree Policy of encoding (RSON).

Data Transfer Control
~~~~~~~~~~~~~~~~~~~~~

Delta-T

* Maximum Packet Lifetime (MPL)
* Maximum Ack delta (A)
* Maximum Retransmit delta (R)


.. seqdiag::
   :alt: A sequence diagram is missing from your view

   seqdiag {
    default_fontsize = 14;
    "Sending App"; "Sending DIF"; "POA"; "Receiving DIF"; "Receiving App";
    === Data Transfer ===
    "Sending App" ->> "Sending DIF" [label="msg"]{
    "Receiving DIF" -> "Sending DIF" [leftnote="MPL expired"];
    }
   }

DTP/DTCP instances are deleted automatically after 2MPL with no traffic,


.. _CDAP: https://github.com/PouzinSociety/tinos/wiki/Common-Distributed-Application-Protocol
