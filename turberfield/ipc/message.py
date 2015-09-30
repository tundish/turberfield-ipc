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
from functools import singledispatch
import inspect
import json
import re
import warnings

import rson

Header = namedtuple("Header", ["id", "src", "dst", "hMax", "via", "hop"])
Message = namedtuple("Message", ["header", "payload"])
Scalar = namedtuple("Scalar", ["name", "unit", "value", "regex", "tip"])

_public = {
    ".".join((
        dict(inspect.getmembers(i)).get("__module__"),
        i.__name__)
    ): i for i in (Header, Scalar)
}

class TypesEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, type(re.compile(""))):
            return obj.pattern

        try:
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        except AttributeError:
            return json.JSONEncoder.default(self, obj)

def obj_to_odict(obj):
    rv = OrderedDict([("_type", obj.__class__.__name__)])
    rv.update(obj._asdict())
    return rv


@singledispatch
def dumps(obj, **kwargs):
    data = obj_to_odict(obj)
    for i in dumps(data, **kwargs):
        yield i

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

def loads(data):
    rv = list(load(data))
    return Message(rv[0], rv[1:])

@singledispatch
def load(arg):
    raise NotImplementedError

@load.register(Header)
def load_header(obj):
    yield obj

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
    raise NotImplementedError
