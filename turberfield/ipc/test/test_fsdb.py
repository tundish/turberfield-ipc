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


from collections import defaultdict
from collections import namedtuple
import getpass
import json
import os.path
import pkg_resources
import tempfile
import unittest
import warnings

from turberfield.ipc.flow import Flow
from turberfield.ipc.fsdb import Resource
from turberfield.ipc.fsdb import token
from turberfield.ipc.fsdb import gather_installed
import turberfield.ipc.policy
from turberfield.ipc.policy import Routing
from turberfield.ipc.types import Address


def references_by_type(refs):
    objects = [Flow.inspect(i) for i in refs]
    rv = defaultdict(list)
    for ref, obj in zip(refs, objects):
        rv[type(obj)].append(ref)
    return rv

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
        rv = token(
            "file://{}".format(self.root.name),
            "test",
            app
        )
        self.assertIsInstance(rv, Resource)
        self.assertEqual(self.root.name, rv.root)
        self.assertEqual(app, rv.application)
        self.assertTrue(os.path.isdir(os.path.join(*rv[0:5])))

    def test_token_other_db(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            rv = token(
                "http://{}".format(self.root.name),
                "test",
                "addisonarches.web"
            )
            self.assertIs(None, rv)
            self.assertTrue(
                issubclass(w[-1].category, UserWarning))
            self.assertIn("file-based", str(w[-1].message))

    def test_find_flow_empty(self):
        tok = token(
            "file://{}".format(self.root.name),
            "test",
            "addisonarches.web"
        )
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
        tok = token(
            "file://{}".format(self.root.name),
            "test",
            "addisonarches.web"
        )
        self.assertIs(None, tok.flow)
        rv = list(Flow.find(tok))
        self.assertFalse(rv)

        self.assertTrue(
            list(gather_installed("turberfield.ipc.poa")),
            "No declared POA endpoints; install package for testing."
        )

        rv = next(Flow.create(tok, poa=["udp"], role=[], routing=[]))
        self.assertEqual("udp", rv.policy)
        self.assertEqual(".json", rv.suffix)

        udp = Flow.inspect(rv)
        self.assertIsInstance(udp.port, int)
        
    def test_create_routing(self):
        tok = token(
            "file://{}".format(self.root.name),
            "test",
            "addisonarches.web"
        )

        refs = list(Flow.create(tok, poa=["udp"], role=[], routing=["application"]))
        features = references_by_type(refs)
        
        routes = features[turberfield.ipc.policy.Routing.Application]
        self.assertEqual(1, len(routes))
        table = Flow.inspect(routes[0])

        self.assertIsInstance(table, turberfield.ipc.policy.Routing.Application)
        self.assertFalse(table)
        
        rule = turberfield.ipc.policy.Routing.Application.Rule(
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.receiver"),
            1,
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.hub")
        )
        self.assertIs(None, table.replace(rule.src, rule.dst, rule))
        self.assertEqual(1, len(table))

        Flow.replace(routes[0], table)
        rv = Flow.inspect(routes[0])
        self.assertEqual(table, rv)

    def test_route_inspection_use_case(self):
        self.test_create_routing()

        tok = token(
            "file://{}".format(self.root.name),
            "test",
            "addisonarches.web"
        )
        search = ((i, Flow.inspect(i)) for i in Flow.find(tok, policy="application"))
        query = (
            ref
            for ref, table in search
            for rule in table
            if rule.dst.application == "turberfield.ipc.demo.receiver"
        )
        self.assertEqual(1, len(list(query)))

    @unittest.skip("Progressively slowing test. Subtest takes ~1sec at n == 500.") 
    def test_pool_allocation(self):
        tok = token(
            "file://{}".format(self.root.name),
            "test",
            "addisonarches.web"
        )

        ports = range(49152, 65536)
        for n, p in enumerate(ports):
            with self.subTest(n=n, p=p):
                flow = list(Flow.create(tok, poa=["udp"], role=[], routing=[]))
                query = (Flow.inspect(i) for i in Flow.find(tok, policy="udp"))
                alloc = {(i.addr, i.port) for i in query}
                self.assertEqual(n + 1, len(alloc))
        
    def test_create_policy_unregistered(self):
        tok = token(
            "file://{}".format(self.root.name),
            "test",
            "addisonarches.web"
        )
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
        tok = token(
            "file://{}".format(self.root.name),
            "test",
            "addisonarches.web"
        )
        self.assertIs(None, tok.flow)
        results = list(Flow.find(tok, application="addisonarches.game"))
        self.assertFalse(results)
