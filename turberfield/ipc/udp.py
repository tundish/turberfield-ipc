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
from turberfield.ipc.message import dumps
from turberfield.ipc.message import loads
from turberfield.ipc.netstrings import dumpb
from turberfield.ipc.netstrings import loadb
from turberfield.ipc.node import TakesPolicy


class UDPAdapter(asyncio.DatagramProtocol):

    def __init__(self, loop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = loop
        self.decoder = loadb(encoding="utf-8")
        self.decoder.send(None)
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        # Routing only here, no service!
        packet = self.decoder.send(data)
        if packet is not None:
            print("Received ", packet)
        #TODO: Access header
        # Do routing

        # Routing only: modify header and send on

        # Message delivery: needs 

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Socket closed, stop the event loop")
        loop = asyncio.get_event_loop()
        loop.stop()

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

                # TODO: Routing delegated to subclass. Mixed in via policy
                # mechanism
                if msg.header.via is not None:
                    # User-defined route
                    route = next(Flow.find(
                        token,
                        application=msg.header.via.application,
                        policy="udp"),
                    None)
                else:
                    raise NotImplementedError
                    
                    #search = ((i, Flow.inspect(i)) for i in Flow.find(token, policy="application"))
                    #query = (
                    #    ref
                    #    for ref, table in search
                    #    for rule in table
                    #    if rule.dst.application == "turberfield.ipc.demo.receiver"
                    #)

                # TODO: Replace hop: 0 with hop: 1
                # TODO: Replace via with own address

                udp = Flow.inspect(route)
                remote_addr = (udp.addr, udp.port)

                data = dumpb("\n".join(dumps(msg)))
                self.transport.sendto(data, remote_addr)
                print('Sent:', data)
            except Exception as e:
                print(e)
                continue
