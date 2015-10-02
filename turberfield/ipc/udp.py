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

    def hop(self, token, msg, policy):
        raise NotImplementedError

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        # Routing only here, no service!
        packet = self.decoder.send(data)
        if packet is not None:
            msg = loads(packet)
            print("Received ", msg)

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
        # Service queues here
        super().datagram_received(data, addr)

    @asyncio.coroutine
    def __call__(self, token):
        while True:
            try:
                print("Waiting...")
                job = yield from self.down.get()

                poa, msg = self.hop(token, job, policy="udp")
                if job.header.via is not None:
                    # User-defined route
                    hop = next(Flow.find(
                        token,
                        application=job.header.via.application,
                        policy="udp"),
                    None)
                    poa = Flow.inspect(hop)

                if msg is not None:
                    remote_addr = (poa.addr, poa.port)
                    data = "\n".join(dumps(msg))
                    print(data)
                    packet = dumpb(data)
                    self.transport.sendto(packet, remote_addr)
                    print('Sent:', packet)
                else:
                    print("No message from hop.")

            except Exception as e:
                print(e)
                continue
