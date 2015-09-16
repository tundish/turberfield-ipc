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
import json
import pkg_resources

import unittest

import turberfield.ipc.policy

def package_interface(key="turberfield.ipc.role"):
    for i in pkg_resources.iter_entry_points(key):
        try:
            ep = i.resolve()
        except Exception as e:
            continue
        else:
            yield (i.name, ep)

Path = namedtuple(
    "Path",
    ["root", "namespace", "user", "service", "application", "flow", "policy", "suffix"]
)

class RecordTests(unittest.TestCase):

    def test_path(self):
        udp = turberfield.ipc.policy.POA.UDP(654)
        tx = turberfield.ipc.policy.Role.TX(500, 50, 50)
        record = json.dumps(vars(tx), indent=0, ensure_ascii=False, sort_keys=False)
        self.fail(
            Path(
                ".turberfield",
                "addisonarches",
                "tundish",
                "demo",
                "addisonarches-web",
                "flow00839",
                "tx",
                ".json"
            )
        )
