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


import textwrap
import unittest

from turberfield.ipc.policy import Routing
from turberfield.ipc.types import Address


class PolicyTests(unittest.TestCase):

    routing = textwrap.dedent(
    """
    [
    [
    [
    "turberfield",
    "tundish",
    "test",
    "turberfield.ipc.demo.sender"
    ],
    [
    "turberfield",
    "tundish",
    "test",
    "turberfield.ipc.demo.receiver"
    ],
    1,
    [
    "turberfield",
    "tundish",
    "test",
    "turberfield.ipc.demo.hub"
    ]
    ],
    [
    [
    "turberfield",
    "tundish",
    "test",
    "turberfield.ipc.demo.sender"
    ],
    [
    "turberfield",
    "tundish",
    "test",
    "turberfield.ipc.demo.sender"
    ],
    1,
    [
    "turberfield",
    "tundish",
    "test",
    "turberfield.ipc.demo.hub"
    ]
    ]
    ]""").lstrip()

    def test_save_routing_address_rule(self):
        table = Routing.Application.from_json(PolicyTests.routing)
        self.assertEqual(
            Routing.Application([
                Routing.Application.Rule(
                    Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
                    Address("turberfield", "tundish", "test", "turberfield.ipc.demo.receiver"),
                    1,
                    Address("turberfield", "tundish", "test", "turberfield.ipc.demo.hub"),
                ),
                Routing.Application.Rule(
                    Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
                    Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
                    1,
                    Address("turberfield", "tundish", "test", "turberfield.ipc.demo.hub"),
                )
            ]),
            table
        )
        self.assertEqual(PolicyTests.routing, table.__json__())

    def test_remove_routing_address_rule(self):
        table = Routing.Application.from_json(PolicyTests.routing)
        self.assertEqual(2, len(table))
        old = table.replace(
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender")
        )
        self.assertEqual(
            Routing.Application.Rule(
                Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
                Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
                1,
                Address("turberfield", "tundish", "test", "turberfield.ipc.demo.hub"),
            ),
            old
        )
        self.assertEqual(1, len(table))

    def test_replace_routing_address_rule(self):
        table = Routing.Application.from_json(PolicyTests.routing)
        self.assertEqual(2, len(table))
        rule = Routing.Application.Rule(
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
            3,
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.receiver")
        )
        old = table.replace(
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
            rule
        )
        self.assertEqual(
            Routing.Application([
                Routing.Application.Rule(
                    Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
                    Address("turberfield", "tundish", "test", "turberfield.ipc.demo.receiver"),
                    1,
                    Address("turberfield", "tundish", "test", "turberfield.ipc.demo.hub")
                ),
                Routing.Application.Rule(
                    Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
                    Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
                    3,
                    Address("turberfield", "tundish", "test", "turberfield.ipc.demo.receiver")
                )
            ]),
            table,
        )

    def test_replace_routing_address_bad_rule(self):
        table = Routing.Application.from_json(PolicyTests.routing)
        self.assertEqual(2, len(table))
        rule = Routing.Application.Rule(
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
            3,
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.receiver"),
        )
        old = table.replace(
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
            Address("turberfield", "tundish", "test", "turberfield.ipc.demo.receiver"),
            rule
        )
        self.assertIs(None, old)
        self.assertEqual(
            Routing.Application.from_json(PolicyTests.routing),
            table
        )
