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

import turberfield.ipc.policy

def package_interface(key="turberfield.ipc.role"):
    for i in pkg_resources.iter_entry_points(key):
        try:
            ep = i.resolve()
        except Exception as e:
            continue
        else:
            yield (i.name, ep)

Resource = namedtuple(
    "Resource",
    ["root", "namespace", "user", "service", "application", "flow", "policy", "suffix"]
)

class Flow:

    @staticmethod
    def create(path:Resource, prefix="flow_", suffix=""):
        if all(path[:4]) and not any(path[5:]):
                parent = os.path.join(*path[:5])
                os.makedirs(parent, exist_ok=True)
                flow = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=parent)
                return path._replace(flow=os.path.basename(flow))
        else:
            return path

    @staticmethod
    def invite(flow:Resource, application:Resource):
        pass

    @staticmethod
    def get_invites(application:Resource):
        """
        Return all open invites.
        """
        pass

    @staticmethod
    def get_applications(flow:Resource):
        """
        Return all applications party to a flow.
        """
        pass

    @staticmethod
    def get_flows(application:Resource):
        """
        Return all flows associated with the application.
        """
        pass

    @staticmethod
    def accept(invite:Resource):
        """
        Accepts an invite.
        """
        pass

    @staticmethod
    def refuse(invite:Resource):
        """
        Refuses an invite.
        """
        pass

def recent_slot(path:Resource):
    slots = [i for i in os.listdir(os.path.join(path.root, path.home))
             if os.path.isdir(os.path.join(path.root, path.home, i))]
    stats = [(os.path.getmtime(os.path.join(path.root, path.home, fP)), fP)
             for fP in slots]
    stats.sort(key=operator.itemgetter(0), reverse=True)
    return Persistent.Resource(
        path.root, path.home, next((i[1] for i in stats), None), path.file)

class FlowTests(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.TemporaryDirectory()

    def tearDown(self):
        if os.path.isdir(self.root.name):
            self.root.cleanup()
        self.assertFalse(os.path.isdir(self.root.name))
        self.root = None

    def test_create(self):
        udp = turberfield.ipc.policy.POA.UDP(654)
        tx = turberfield.ipc.policy.Role.TX(500, 50, 50)
        record = json.dumps(vars(tx), indent=0, ensure_ascii=False, sort_keys=False)
        rv = Flow.create(
            Resource(
                ".turberfield", "addisonarches", getpass.getuser(),
                "test", "addisonarches-web",
                None, None, None
            )
        )
        self.assertTrue(rv.flow)
        self.assertTrue(os.path.isdir(os.path.join(*rv[0:5])))

    def test_attach(self):
        udp = turberfield.ipc.policy.POA.UDP(654)
        tx = turberfield.ipc.policy.Role.TX(500, 50, 50)
        record = json.dumps(vars(tx), indent=0, ensure_ascii=False, sort_keys=False)
        master = Resource(
            ".turberfield", "turberfield", getpass.getuser(),
            "test", "turberfield-master",
            None, None, None
        )
        slave = Resource(
            ".turberfield", "turberfield", getpass.getuser(),
            "test", "turberfield-slave",
            None, None, None
        )
        flow = Flow.create(master)
        rv = Flow.invite(flow, slave)
        self.assertTrue(rv)
