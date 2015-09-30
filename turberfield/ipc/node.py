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

import asyncio
from collections import defaultdict
from collections import namedtuple
import logging
import warnings

from turberfield.ipc.flow import Flow

# TODO: resite
Policy = namedtuple("Policy", ["poa", "role", "routing"])

class TakesPolicy:

    def __init__(self, *args, **kwargs):
        self.policy = Policy(*(kwargs.pop(i) for i in Policy._fields))
        super().__init__(*args, **kwargs)
            

class UDPAdapter(asyncio.DatagramProtocol):

    def __init__(self, loop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = loop
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        # Routing only here, no service!
        message = data.decode()
        #TODO: De-frame
        # Retrieve user name from header (simulate login)
        # Retrieve application name from header
        # Get flow -> addr.
        print('Received %r from %s' % (message, addr))
        print('Send %r to %s' % (message, addr))
        self.transport.sendto(data, addr)

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Socket closed, stop the event loop")
        loop = asyncio.get_event_loop()
        loop.stop()

# TODO: conform to interface of turberfield.ipc.mechanism.POA
class UDPService(UDPAdapter, TakesPolicy):

    def __init__(self, loop, down=None, up=None, *args, **kwargs):
        super().__init__(loop, *args, **kwargs)
        self.down = down
        self.up = up

    def datagram_received(self, data, addr):
        super().datagram_received(data, addr)
        # Service queues here

    @asyncio.coroutine
    def __call__(self, token):
        while True:
            try:
                print("Waiting...")
                msg = yield from self.down.get()

                hdr = msg[0]
                #msg[0] = hdr._replace()

                # TODO: Two chances; local instance or route to external instance
                route = next(Flow.find(token, application=hdr.next, policy="udp"), None)
                #search = ((i, Flow.inspect(i)) for i in Flow.find(token, policy="application"))
                #query = (
                #    ref
                #    for ref, table in search
                #    for rule in table
                #    if rule.dst.application == "turberfield.ipc.demo.receiver"
                #)
                while route is None:
                    self.log.warning("No route for {}".format(hdr.next))
                    yield from asyncio.sleep(3, loop=self.loop)
                    route = next(Flow.find(token, application=hdr.next, policy="udp"), None)

                udp = Flow.inspect(route)
                print(udp)
                remote_addr = (udp.addr, udp.port)

                # TODO: Sequence -> RSON
                # TODO: Framing
                print('Send:', msg)
                for unit in msg[1:]:
                    self.transport.sendto(unit.encode(), addr=remote_addr)
            except Exception as e:
                print(e)
                continue

def create_udp_node(loop, token, down, up):
    """
    Creates a node which uses UDP for inter-application messaging

    """
    assert loop.__class__.__name__.endswith("SelectorEventLoop")
 
    services = set()
    policies = Policy(poa=["udp"], role=[], routing=["application"])
    for ref in Flow.create(token, **vars(policies)):
        obj = Flow.inspect(ref)
        key = next(k for k, v in vars(policies).items() if ref.policy in v) 
        field = getattr(policies, key)
        field[field.index(ref.policy)] = obj
        try:
            services.add(obj.mechanism)
        except AttributeError:
            warnings.warn("Policy '{}' lacks a mechanism".format(ref.policy))

    udp = next(iter(policies.poa))
    Mixin = type("UdpNode", tuple(services), {})
    transport, protocol = loop.run_until_complete(
        loop.create_datagram_endpoint(
            lambda:Mixin(loop, down=down, up=up, **vars(policies)),
            local_addr=(udp.addr, udp.port)
        )
    )
    return protocol
