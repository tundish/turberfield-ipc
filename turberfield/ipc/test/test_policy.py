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


class PolicyTests(unittest.TestCase):

    def test_routing_address_rule(self):
        dump = textwrap.dedent("""
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
        ]""")
        table = Routing.Application.from_json(dump)
        self.assertEqual(
            Routing.Application([
                Routing.Application.Rule(
                    Routing.Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
                    Routing.Address("turberfield", "tundish", "test", "turberfield.ipc.demo.receiver"),
                    1,
                    Routing.Address("turberfield", "tundish", "test", "turberfield.ipc.demo.hub"),
                ),
                Routing.Application.Rule(
                    Routing.Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
                    Routing.Address("turberfield", "tundish", "test", "turberfield.ipc.demo.sender"),
                    1,
                    Routing.Address("turberfield", "tundish", "test", "turberfield.ipc.demo.hub"),
                )
            ]),
            table)
