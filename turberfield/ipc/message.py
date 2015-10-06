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
Registering application objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To include your own classes in message transmissions, you must register them
with these two generators:

* turberfield.ipc.message.dumps_
* turberfield.ipc.message.load_

And optionally with this function:

* turberfield.ipc.message.replace_

::

    Alert = namedtuple("Alert", ["ts", "text"])

    @load.register(Alert)
    def load_alert(obj):
        yield obj._replace(
            ts=datetime.strptime(obj.ts, "%Y-%m-%d %H:%M:%S"),
        )

"""

Address = turberfield.ipc.types.Address
Header = namedtuple("Header", ["id", "src", "dst", "hMax", "via", "hop"])
Message = namedtuple("Message", ["header", "payload"])
Alert = namedtuple("Alert", ["ts", "text"])
Scalar = namedtuple("Scalar", ["name", "unit", "value", "regex", "tip"])

_public = type_dict(Alert, Header, Scalar)

def parcel(token, *args, dst=None, via=None, hMax=3):
    hdr = Header(
        id=uuid.uuid4().hex,
        src=Address(**{i: getattr(token, i, None) for i in Address._fields}),
        dst=dst or Address(**{i: getattr(token, i, None) for i in Address._fields}),
        hMax=hMax,
        via=via,
        hop=0,
    )
    return Message(hdr, args)


@singledispatch
def dumps(obj, **kwargs):
    try:
        data = obj_to_odict(obj)
    except AttributeError:
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

def loads(data):
    rv = list(load(data))
    try:
        return Message(rv[0], rv[1:])
    except IndexError:
        return Message(None, [])

@singledispatch
def load(arg):
    raise NotImplementedError

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
def load_dict(data, types=_public):
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
    except TypeError:
        warnings.warn(
            "Parameter mismatch against {}".format(typ.__name__)
        )

@load.register(list)
def load_list(data):
    for obj in data:
        yield load(obj)

@load.register(str)
def load_str(data):
    bits = rson.loads(data)
    items = bits if isinstance(bits, list) else [bits]
    for n, item in enumerate(items):
        try:
            for obj in load(item):
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
