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
import getpass
import json
import os.path
import pkg_resources
import tempfile
import unittest
import warnings

from turberfield.ipc.flow import gather_from_installation
from turberfield.ipc.flow import Flow
from turberfield.ipc.fsdb import Resource
from turberfield.ipc.fsdb import token
import turberfield.ipc.policy


class FlowTests(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.TemporaryDirectory()

    def tearDown(self):
        if os.path.isdir(self.root.name):
            self.root.cleanup()
        self.assertFalse(os.path.isdir(self.root.name))
        self.root = None

    def test_token_file_db(self):
        app = "addisonarches.web"
        rv = token("file://{}".format(self.root.name), app)
        self.assertIsInstance(rv, Resource)
        self.assertEqual(self.root.name, rv.root)
        self.assertEqual(app, rv.application)
        self.assertTrue(os.path.isdir(os.path.join(*rv[0:5])))

    def test_token_other_db(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            rv = token("http://{}".format(self.root.name), "addisonarches.web")
            self.assertIs(None, rv)
            self.assertTrue(
                issubclass(w[-1].category, UserWarning))
            self.assertIn("file-based", str(w[-1].message))

    def tost_create(self):
        udp = turberfield.ipc.policy.POA.UDP(654)
        tx = turberfield.ipc.policy.Role.TX(500, 50, 50)
        record = json.dumps(vars(tx), indent=0, ensure_ascii=False, sort_keys=False)
        rv = Flow.create(
            Resource(
                ".turberfield", "addisonarches", getpass.getuser(),
                "test", "addisonarches-web",
                None, None, None
            ),
            poa=None,
        )
        self.assertTrue(rv.flow)
        self.assertTrue(os.path.isdir(os.path.join(*rv[0:5])))

    def test_find_flow_empty(self):
        tok = token("file://{}".format(self.root.name), "addisonarches.web")
        self.assertIs(None, tok.flow)
        rv = list(Flow.find(tok))
        self.assertFalse(rv)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("ignore")
            rv = next(Flow.create(tok, poa=[], role=[], routing=[]), None)
            self.assertIs(None, rv)

        results = list(Flow.find(tok))
        self.assertFalse(results)
        
    def test_create_policy(self):
        tok = token("file://{}".format(self.root.name), "addisonarches.web")
        self.assertIs(None, tok.flow)
        rv = list(Flow.find(tok))
        self.assertFalse(rv)

        self.assertTrue(
            list(gather_from_installation("turberfield.ipc.poa")),
            "No declared POA endpoints; install package for testing."
        )

        rv = next(Flow.create(tok, poa=["udp"], role=[], routing=[]))
        self.assertEqual("udp", rv.policy)
        self.assertEqual(".json", rv.suffix)

        udp = Flow.inspect(rv)
        self.assertIsInstance(udp.port, int)
        
    def test_create_policy_unregistered(self):
        tok = token("file://{}".format(self.root.name), "addisonarches.web")
        self.assertIs(None, tok.flow)
        rv = next(Flow.find(tok), None)
        self.assertIs(None, rv)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            rv = next(Flow.create(tok, poa=["ftp"], role=[], routing=[]))
            self.assertIs(None, rv)
            self.assertTrue(
                issubclass(w[-1].category, UserWarning))
            self.assertIn("No policy", str(w[-1].message))
        
    def test_find_application(self):
        tok = token("file://{}".format(self.root.name), "addisonarches.web")
        self.assertIs(None, tok.flow)
        results = list(Flow.find(tok, application="addisonarches.game"))
        self.assertFalse(results)
