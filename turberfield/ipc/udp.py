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
import concurrent.futures
import functools
import warnings

from turberfield.ipc.flow import Flow
from turberfield.ipc.netstrings import dumpb
from turberfield.ipc.netstrings import loadb
from turberfield.ipc.node import TakesPolicy

from turberfield.utils.assembly import Assembly

class UDPAdapter(asyncio.DatagramProtocol):

    def __init__(self, loop, token, types, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = loop
        self.token = token
        self.types = types
        self.decoder = loadb(encoding="utf-8")
        self.decoder.send(None)
        self.transport = None

    def hop(self, token, msg, policy):
        raise NotImplementedError

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        """
        Routing only. Provides no upward service.

        """
        packet = self.decoder.send(data)
        if packet is None:
            return (None, None)

        msg = Assembly.loads(packet)
        poa, msg = self.hop(self.token, msg, policy="udp")
        if poa is not None:
            remote_addr = (poa.addr, poa.port)
            data = Assembly.dumps(msg)
            packet = dumpb(data)
            self.transport.sendto(packet, remote_addr)
        return (poa, msg)

    def error_received(self, exc):
        warnings.warn(exc)

    def connection_lost(self, exc):
        warnings.warn("Socket closed.")

class UDPService(UDPAdapter, TakesPolicy):

    def __init__(self, loop, token, types, down=None, up=None, *args, **kwargs):
        super().__init__(loop, token, types, *args, **kwargs)
        self.down = down
        self.up = up

    def datagram_received(self, data, addr):
        """
        Extends routing function to serve messages upward.

        """
        poa, msg = super().datagram_received(data, addr)
        if msg is not None:
            self.loop.call_soon_threadsafe(functools.partial(self.up.put_nowait, msg))

    @asyncio.coroutine
    def __call__(self, token=None):
        token = token or self.token
        while True:
            try:
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

                if poa is None:
                    warnings.warn("Message expired.")
                    continue

                if msg is not None:
                    remote_addr = (poa.addr, poa.port)
                    data = Assembly.dumps(msg)
                    packet = dumpb(data)
                    self.transport.sendto(packet, remote_addr)
                else:
                    warnings.warn("No message from hop.")

            except concurrent.futures.CancelledError:
                break
            except Exception as e:
                warnings.warn(repr(getattr(e, "args", e) or e))
                continue
