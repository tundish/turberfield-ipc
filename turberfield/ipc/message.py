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

import rson

import turberfield.ipc.types
from turberfield.utils.misc import TypesEncoder
from turberfield.utils.misc import obj_to_odict
from turberfield.utils.misc import type_dict

__doc__ = """
To customise the way your classes are loaded from a received message, you must register them
with this generator:

* turberfield.ipc.message.load_

and optionally with:

* turberfield.ipc.message.dumps_
* turberfield.ipc.message.replace_

For example, here's how the :py:mod:`message <turberfield.ipc.message>` module defines its
own `Alert` class::

    Alert = namedtuple("Alert", ["ts", "text"])

And this is how it customises the deserialising of these objects so
that its `ts` attribute is itself loaded as Python object::

    @load.register(Alert)
    def load_alert(obj):
        yield obj._replace(
            ts=datetime.strptime(obj.ts, "%Y-%m-%d %H:%M:%S"),
        )

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

_public = type_dict(Alert, Header, Scalar)
registry = _public

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
    :param header: The Header object of the origin message.
    :param args: Application objects to send in the message.
    :param dst: An :py:class:`Address <turberfield.ipc.types.Address>` for the destination.
                If `None`, will be set to the source address (ie: a loopback message).
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


@singledispatch
def dumps(obj, **kwargs):
    """
    This generator takes a single object as its first argument.
    It dispatches by type to a handler which serialises the object as RSON.

    """
    try:
        data = obj_to_odict(obj)
    except AttributeError as e:
        warnings.warn(
            "Dump issue {0} ({1!r})".format(
                obj, e
            )
        )
        yield obj
    else:
        yield from dumps(data, **kwargs)

@dumps.register(dict)
def dumps_dict(obj, indent=0):
    yield json.dumps(
        obj,
        cls=TypesEncoder,
        indent=indent
    )

@dumps.register(list)
def dumps_list(objs):
    for obj in objs:
        for content in dumps(obj):
            yield content

@dumps.register(Message)
def dumps_message(obj):
    yield from dumps([obj.header, *obj.payload])

def loads(data, **kwargs) -> Message:
    """
    Use this function to parse an RSON string as a message.

    The optional `types` keyword allows you to specify which classes you expect
    to load. It's a dictionary mapping the class to its fully-qualified name.

    The helper function :py:func:`turberfield.utils.misc.type_dict` can make one
    of these for you::

        types = turberfield.utils.misc.type_dict(
            turberfield.ipc.message.Alert,
            turberfield.ipc.message.Header
        )
        msg = turberfield.ipc.message.loads(data, types=types)

    """
    rv = list(load(data, **kwargs))
    try:
        return Message(rv[0], rv[1:])
    except IndexError:
        return Message(None, [])

@singledispatch
def load(arg, **kwargs):
    """
    This generator function recursively dispatches on the type of its first argument
    (initially an RSON string).
    It yields application-specific objects.

    """
    yield arg

@load.register(Alert)
def load_alert(obj):
    yield obj._replace(
        ts=datetime.strptime(obj.ts, "%Y-%m-%d %H:%M:%S"),
    )

@load.register(Header)
def load_header(obj):
    yield obj._replace(
        src=Address(*obj.src),
        dst=Address(*obj.dst),
        via=Address(*obj.via),
    )

@load.register(Scalar)
def load_scalar(obj):
    yield obj._replace(regex=re.compile(obj.regex))

@load.register(dict)
def load_dict(data, types=registry):
    name = data.pop("_type", None)
    try:
        typ = types[name]
    except KeyError:
        warnings.warn(
            "Type '{}' not recognised".format(name)
        )
        raise
    try:
        for obj in load(typ(**data)):
            yield obj
    except TypeError as e:
        warnings.warn(
            "Parameter mismatch against {0} ({1!r}): {2}".format(
                typ.__name__, e, data
            )
        )

@load.register(list)
def load_list(data):
    for obj in data:
        yield load(obj)

@load.register(str)
def load_str(data, **kwargs):
    bits = rson.loads(data)
    items = bits if isinstance(bits, list) else [bits]
    for n, item in enumerate(items):
        try:
            for obj in load(item, **kwargs):
                yield obj
        except KeyError:
            warnings.warn(
                "No load of item {}".format(n + 1)
            )
        except IndexError:
            warnings.warn(
                "Missing data in {}".format(n + 1)
            )

@load.register(bytes)
def load_bytes(data):
    yield from load(data.decode("utf-8"))

@singledispatch
def replace(obj, seq):
    """
    Finds in the sequence `seq` an existing object corresponding to the argument
    `obj`. Replaces such an item in the sequence with `obj`, and returns a 2-tuple
    of (`existing`, `seq`).

    The equivalence of objects is application-specific.
    """
    raise NotImplementedError
