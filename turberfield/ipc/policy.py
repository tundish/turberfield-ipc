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
import random

from turberfield.ipc.flow import Flow
from turberfield.ipc.flow import Pooled
import turberfield.ipc.node

# TODO: resite
class SavesToJSON:

    @classmethod
    def from_json(cls, data):
        return cls(**json.loads(data))

    def __json__(self):
        return json.dumps(vars(self), indent=0, ensure_ascii=False, sort_keys=False)

class POA:
    """
        Advertised through turberfield.ipc.poa entry point.

    """
    class UDP(Pooled, SavesToJSON):

        mechanism = turberfield.ipc.node.UDPService

        @classmethod
        def allocate(cls, others=[], pool=slice(49152, 65535)):
            print(others)
            return cls(random.randint(pool.start, pool.stop))

        def __init__(self, port, addr="127.0.0.1"):
            self.port = port
            self.addr = addr

class Routing:
    """
        Advertised through turberfield.ipc.routing entry point.

    """
    Address = namedtuple(
        "Address",
        ["namespace", "user", "service", "application"]
    )

    class Namespace:
        """
        Routing aggregated to the namespace domain. Messages going here
        indicate a need to extend trust. Might route to, eg, a matchmaker
        service.

        """
        pass

    class User:
        """
        Routing information to the user domain. Messages going here
        indicate a need to coordinate operations. Might route to, eg: a
        monitoring service.

        """
        pass

    class Service:
        """
        Routing information to the service domain. Messages going here
        indicate a need to register applications. Might route to, eg: a
        discovery service.

        """
        pass

    class Application:

        @classmethod
        def from_json(cls, data):
            return cls(**json.loads(data))

        def __json__(self):
            return json.dumps(vars(self), indent=0, ensure_ascii=False, sort_keys=False)

        def __init__(self, src:"Routing.Address", dst:"Routing.Address", via:"Routing.Address"):
            self.src = src
            self.dst = dst
            self.via = via


class Role:
    """
        Advertised through turberfield.ipc.role entry point.

    """
    class RX(SavesToJSON):

        def __init__(self, tMaxPdu=5.0, tMaxAck=0.5, tMaxRtx=11.0):
            self.tMaxPdu = tMaxPdu
            self.tMaxAck = tMaxAck
            self.tMaxRtx = tMaxRtx

    class TX(SavesToJSON):

        def __init__(self, tMaxPdu=5.0, tMaxAck=0.5, tMaxRtx=11.0):
            self.tMaxPdu = tMaxPdu
            self.tMaxAck = tMaxAck
            self.tMaxRtx = tMaxRtx
