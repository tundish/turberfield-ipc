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
import itertools
import json
import os.path
import tempfile
import textwrap
import unittest
import warnings

#from turberfield.ipc.assembly import Assembly
import turberfield.ipc.message
import turberfield.ipc.types
from turberfield.utils.misc import type_dict

import rson

class Assembly:

    @staticmethod
    def elements(obj, names=[], verbose=True):
        try:
            data = obj._asdict()
        except (AttributeError, TypeError):
            try:
                data = vars(obj)
            except TypeError:
                if isinstance(obj, list):
                    for item in obj:
                        yield from Assembly.elements(
                            item, names=names
                        )
                elif verbose:
                    yield (".".join(names), obj)
                else:
                    yield (names[-1], obj)
                return

        for key, val in sorted(data.items()):
            yield from Assembly.elements(
                val, names=names[:] + [key]
            )


class Wheelbarrow(Assembly):

    Bucket = namedtuple("Bucket", ["capacity"])
    Grip = namedtuple("Grip", ["length", "colour"])
    Handle = namedtuple("Handle", ["length", "grip"])
    Rim = namedtuple("Rim", ["dia"])
    Tyre = namedtuple("Tyre", ["dia", "pressure"])
    Wheel = namedtuple("Wheel", ["rim", "tyre"])

    def __init__(self, bucket=None, wheel=None, handles=[]):
        self.bucket = bucket
        self.wheel = wheel
        self.handles = handles


    def feed(self, *args):
        objs = iter(args)
        try:
            while not self.bucket:
                obj = next(objs)
                self.bucket = Wheelbarrow.Bucket(**obj)
            while not self.wheel:
                self.wheel = Wheelbarrow.Wheel(
                    Wheelbarrow.Rim(**next(objs)),
                    Wheelbarrow.Tyre(**next(objs))
                )
            while True:
                self.handles.append(
                    Wheelbarrow.Handle(
                        length=next(objs).get("length", None),
                        grip=Wheelbarrow.Grip(**next(objs))
                    )
                )
        finally:
            return self

class AssemblyTester(unittest.TestCase):

    def test_single_assembly_load(self):
        data = textwrap.dedent("""
        {
        _type: turberfield.ipc.test.test_assembly.Wheelbarrow
        }
        {
        capacity: 45
        }
        {
        dia: 40
        }
        {
        dia: 40,
        pressure: 30
        }
        {
        length: 80
        }
        {
        length: 15,
        colour: green
        }
        {
        length: 80
        }
        {
        length: 15,
        colour: green
        }
        """)

        def load(data, types={}, loader=json.loads):
            rv = None
            items = [
                (types.get(i.pop("_type", None), dict), i)
                for i in loader(data)
            ]
            indexes = [
                n
                for n, (t, i) in enumerate(items)
                if issubclass(t, (Assembly,))
            ]
            chunks = [
                slice(a, b)
                for a, b in zip(indexes, indexes[1:] + [len(items)])
            ]

            n = 0
            bits = enumerate(items)
            while True:
                try:
                    chunk = chunks.pop(0)
                    while n < chunk.start:
                        n, (typ, item) = next(bits)
                        yield typ(**item)

                    n, (typ, item) = next(bits)
                    rv = typ(**item)
                    rv.feed(*[
                        typ(**item)
                        for n, (typ, item) in itertools.islice(
                            bits, chunk.stop - chunk.start
                        )
                    ])
                    yield rv
                except IndexError:
                    while n < len(items):
                        n, (typ, item) = next(bits)
                        yield typ(**item)
                    else:
                        return

        types = type_dict(Wheelbarrow, namespace="turberfield")
        rv = next(load(data, types=types, loader=rson.loads), None)
        self.assertIsInstance(rv, Wheelbarrow)
        self.assertEqual(45, rv.bucket.capacity)
        self.assertEqual(30, rv.wheel.tyre.pressure)
        self.assertEqual("green", rv.handles[1].grip.colour)
        print(*list(rv.elements(rv)), sep="\n")

        def default(obj):
            return list(obj.elements(obj))

        print(json.dumps(rv, default=default))

    def test_multiple_assemblies(self):
        data = textwrap.dedent("""
        {
        _type: turberfield.ipc.test.test_assembly.Wheelbarrow
        }
        {
        _type: turberfield.ipc.test.test_assembly.Wheelbarrow
        }
        """)
