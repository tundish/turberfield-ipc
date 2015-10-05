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
import warnings

import turberfield.ipc.delivery
from turberfield.ipc.flow import Flow
from turberfield.ipc.flow import Pooled
from turberfield.ipc.types import Address
import turberfield.ipc.udp
from turberfield.utils.misc import SavesAsDict
from turberfield.utils.misc import SavesAsList


class POA:
    """
        Advertised through turberfield.ipc.poa entry point.

    """
    class UDP(Pooled, SavesAsDict):

        mechanism = turberfield.ipc.udp.UDPService

        @classmethod
        def allocate(cls, addr="127.0.0.1", ports=slice(49152, 65535, 1), others=[]):
            taken = {(i.addr, i.port) for i in others}
            pool = {(addr, i) for i in range(ports.start, ports.stop, ports.step)}
            return cls(*(pool - taken).pop())

        def __init__(self, addr, port):
            self.addr = addr
            self.port = port

class Routing:
    """
        Advertised through turberfield.ipc.routing entry point.

    """

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

        mechanism = turberfield.ipc.delivery.PeerRouter

        Rule = namedtuple("Rule", ["src", "dst", "hMax", "via"])

        @classmethod
        def from_json(cls, data):
            return cls(
                [cls.Rule(*[class_(item) if class_ is int else class_(*item)
                for item, class_ in zip(rule, (Address, Address, int, Address))]) 
                for rule in json.loads(data)]
            )

        def replace(self, src, dst, rule=None):
            matches = [(n, i) for n, i in enumerate(self) if i.src == src and i.dst == dst]
            if len(matches) > 1:
                warnings.warn("Duplicate rules for {0}, {1} in table".format(src, dst))

            try:
                index, rv = next(iter(matches))
            except StopIteration:
                index, rv = (0, None)
            
            if rule is None:
                del self[index]
            elif isinstance(rule, self.Rule) and (rule.src, rule.dst)  == (src, dst):
                try:
                    self[index] = rule
                except IndexError:
                    self.insert(index, rule)
            else:
                rv = None
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
