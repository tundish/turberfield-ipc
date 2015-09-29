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
import warnings

from turberfield.ipc.flow import Flow
from turberfield.ipc.flow import Pooled
import turberfield.ipc.node

# TODO: resite
class SavesAsDict:

    @classmethod
    def from_json(cls, data):
        return cls(**json.loads(data))

    def __json__(self):
        return json.dumps(vars(self), indent=0, ensure_ascii=False, sort_keys=False)

 
class SavesAsList:

    @classmethod
    def from_json(cls, data):
        return cls(json.loads(data))

    def __json__(self):
        return json.dumps(self, indent=0, ensure_ascii=False, sort_keys=False)

class POA:
    """
        Advertised through turberfield.ipc.poa entry point.

    """
    class UDP(Pooled, SavesAsDict):

        mechanism = turberfield.ipc.node.UDPService

        @classmethod
        def allocate(cls, others=[], pool=slice(49152, 65535)):
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

    class Application(list, SavesAsList):

        Rule = namedtuple("Rule", ["src", "dst", "hMax", "via"])

        @classmethod
        def from_json(cls, data):
            return cls(
                [cls.Rule(*[class_(item) if class_ is int else class_(*item)
                for item, class_ in zip(rule, (Routing.Address, Routing.Address, int, Routing.Address))]) 
                for rule in json.loads(data)]
            )

        def replace(self, src, dst, rule=None):
            rv = None
            matches = [(n, i) for n, i in enumerate(self) if i.src == src and i.dst == dst]
            if len(matches) > 1:
                warnings.warn("Duplicate rules for {0}, {1} in table".format(src, dst))

            try:
                index, rv = next(iter(matches))
            except StopIteration:
                pass
            else:
                if rule is None:
                    del self[index]
                elif (getattr(rule, "src", rule[0]), getattr(rule, "dst", rule[1]))  == (src, dst):
                    self[index] = rule
                else:
                    rv = None
            finally:
                return rv

class Role:
    """
        Advertised through turberfield.ipc.role entry point.

    """
    class RX(SavesAsDict):

        def __init__(self, tMaxPdu=5.0, tMaxAck=0.5, tMaxRtx=11.0):
            self.tMaxPdu = tMaxPdu
            self.tMaxAck = tMaxAck
            self.tMaxRtx = tMaxRtx

    class TX(SavesAsDict):

        def __init__(self, tMaxPdu=5.0, tMaxAck=0.5, tMaxRtx=11.0):
            self.tMaxPdu = tMaxPdu
            self.tMaxAck = tMaxAck
            self.tMaxRtx = tMaxRtx
