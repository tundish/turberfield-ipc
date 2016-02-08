#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.


from collections import namedtuple
from datetime import datetime
from functools import singledispatch
import json
import re
import uuid
import warnings

import turberfield.ipc.types
from turberfield.utils.assembly import Assembly

__doc__ = """
To enable your objects to go into a message, you must register
their classes with `turberfield.utils.assembly.Assembly`.

For example, here's how the :py:mod:`message <turberfield.ipc.message>` module defines its
own `Alert` class::

    Alert = namedtuple("Alert", ["ts", "text"])

And this is how it registers these objects so they can be dumped into
a message and loaded back::

    Assembly.register(Alert)

"""

Address = turberfield.ipc.types.Address
Header = namedtuple("Header", ["id", "src", "dst", "hMax", "via", "hop"])
Alert = namedtuple("Alert", ["ts", "text"])
Scalar = namedtuple("Scalar", ["name", "unit", "value", "regex", "tip"])

Message = namedtuple("Message", ["header", "payload"])
Message.__doc__ = """`{}`

An Message object holds both protocol control information (PCI) and
application data.

    header
        PCI data necessary for the delivery of the message.
    payload
        Client data destined for the application endpoint.
""".format(Message.__doc__)

Assembly.register(Alert, Header, Message, Scalar)

def parcel(token, *args, dst=None, via=None, hMax=3):
    """
    :param token: A DIF token. Just now the function
                  `turberfield.ipc.fsdb.token`_ is the source of these.
    :param args: Application objects to send in the message.
    :param dst: An :py:class:`Address <turberfield.ipc.types.Address>` for the destination.
                If `None`, will be set to the source address (ie: a loopback message).
    :param via: An :py:class:`Address <turberfield.ipc.types.Address>` to
                pass the message on to. If `None`, the most direct route is selected.
    :param hMax: The maximum number of node hops permitted for this message.
    :rtype: Message


    """
    hdr = Header(
        id=uuid.uuid4().hex,
        src=Address(**{i: getattr(token, i, None) for i in Address._fields}),
        dst=dst or Address(**{i: getattr(token, i, None) for i in Address._fields}),
        hMax=hMax,
        via=via,
        hop=0,
    )
    return Message(hdr, args)

def reply(header, *args, dst=None, via=None, hMax=3):
    """
    :param header: The Header object of the original message.
    :param args: Application objects to send in the message.
    :param dst: An :py:class:`Address <turberfield.ipc.types.Address>` for the destination.
                If `None`, will be set to the source address.
    :param via: An :py:class:`Address <turberfield.ipc.types.Address>` to
                pass the message on to. If `None`, the most direct route is selected.
    :param hMax: The maximum number of node hops permitted for this message.
    :rtype: Message


    """
    hdr = Header(
        id=header.id,
        src=header.dst,
        dst=dst or header.src,
        hMax=hMax,
        via=via,
        hop=0,
    )
    return Message(hdr, args)
