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


import os.path
import tempfile
import textwrap
import unittest
import warnings

from turberfield.ipc.fsdb import token
import turberfield.ipc.message
import turberfield.ipc.types

from turberfield.utils.assembly import Assembly


class MessageTester(unittest.TestCase):

    def test_loads_empty_payload(self):
        data = textwrap.dedent("""
        {
        "_type": "turberfield.ipc.message.Message",
        "header": {
            "_type": "turberfield.ipc.message.Header",
            "id": "aa27e84fa93843658bfcd5b4f9ceee4f",
            "src": {
                "_type": "turberfield.ipc.types.Address",
                "namespace": "turberfield",
                "user": "tundish",
                "service": "test",
                "application": "turberfield.ipc.demo.sender"
            },
            "dst": {
                "_type": "turberfield.ipc.types.Address",
                "namespace": "turberfield",
                "user": "tundish",
                "service": "test",
                "application": "turberfield.ipc.demo.receiver"
            },
            "hMax": 3,
            "via": {
                "_type": "turberfield.ipc.types.Address",
                "namespace": "turberfield",
                "user": "tundish",
                "service": "test",
                "application": "turberfield.ipc.demo.hub"
            },
            "hop": 0
        },
        "payload": []
        }
        """)
        msg = Assembly.loads(data)
        self.assertIsInstance(msg, turberfield.ipc.message.Message)
        self.assertIsInstance(msg.header, turberfield.ipc.message.Header)
        self.assertIsInstance(msg.header.src, turberfield.ipc.types.Address)
        self.assertEqual("turberfield.ipc.demo.sender", msg.header.src.application)
        self.assertIsInstance(msg.header.dst, turberfield.ipc.types.Address)
        self.assertEqual("turberfield.ipc.demo.receiver", msg.header.dst.application)
        self.assertIsInstance(msg.header.via, turberfield.ipc.types.Address)
        self.assertEqual("turberfield.ipc.demo.hub", msg.header.via.application)
        self.assertIsInstance(msg.payload, list)
        self.assertFalse(msg.payload)

    @unittest.skip("New behaviour. Test to be redefined.")
    def test_loads_bad_header(self):
        data = textwrap.dedent("""
        {
        "_type": "turberfield.ipc.message.Message",
        "header": {
            "_type": "turberfield.ipc.message.Header",
            "id": "aa27e84fa93843658bfcd5b4f9ceee4f",
            "src": {
                "_type": "turberfield.ipc.types.Address",
                "namespace": "turberfield",
                "user": "tundish",
                "service": "test",
                "application": "turberfield.ipc.demo.sender"
            },
            "dst": {
                "_type": "turberfield.ipc.types.Address",
                "namespace": "turberfield",
                "user": "tundish",
                "service": "test",
                "application": "turberfield.ipc.demo.receiver"
            },
            "hMax": 3,
            "hop": 0
        },
        "payload": []
        }
        """)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            msg = Assembly.loads(data)
            self.assertEqual(1, len(w))
            self.assertTrue(
                issubclass(w[-1].category, UserWarning))
            self.assertIn("Parameter mismatch", str(w[-1].message))

    @unittest.skip("New behaviour. Test to be redefined.")
    def test_loads_bogus_header(self):
        data = textwrap.dedent("""
        {
        "_type": "turberfield.ipc.message.Message",
        "header": {
            "_type": "turberfield.ipc.message.Bogus",
            "id": "aa27e84fa93843658bfcd5b4f9ceee4f",
            "src": {
                "_type": "turberfield.ipc.types.Address",
                "namespace": "turberfield",
                "user": "tundish",
                "service": "test",
                "application": "turberfield.ipc.demo.sender"
            },
            "dst": {
                "_type": "turberfield.ipc.types.Address",
                "namespace": "turberfield",
                "user": "tundish",
                "service": "test",
                "application": "turberfield.ipc.demo.receiver"
            },
            "hMax": 3,
            "via": {
                "_type": "turberfield.ipc.types.Address",
                "namespace": "turberfield",
                "user": "tundish",
                "service": "test",
                "application": "turberfield.ipc.demo.hub"
            },
            "hop": 0
        },
        "payload": []
        }
        """)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            msg = Assembly.loads(data)
            self.assertEqual(2, len(w))
            self.assertTrue(
                issubclass(w[-1].category, UserWarning))
            self.assertIn("not recognised", str(w[0].message))

class AddressingTester(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.TemporaryDirectory()

    def tearDown(self):
        if os.path.isdir(self.root.name):
            self.root.cleanup()
        self.assertFalse(os.path.isdir(self.root.name))
        self.root = None

    def test_address_no_via(self):
        app = "addisonarches.web"
        tok = token(
            "file://{}".format(self.root.name),
            "test",
            app
        )
        msg = turberfield.ipc.message.parcel(tok, {"text": "Hello World!"})
        self.assertEqual(app, msg.header.src.application)
        self.assertEqual(msg.header.src, msg.header.dst)
        self.assertIs(None, msg.header.via)

    def test_reply(self):
        app = "addisonarches.web"
        tok = token(
            "file://{}".format(self.root.name),
            "test",
            app
        )
        msg = turberfield.ipc.message.parcel(tok, {"text": "Hello World!"})
        reply = turberfield.ipc.message.reply(msg.header, {"text": "Goodbye World!"})
        self.assertEqual(msg.header.id, reply.header.id)
        self.assertEqual(msg.header.src, reply.header.dst)
        self.assertEqual(msg.header.dst, reply.header.src)
