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

import argparse
import asyncio
import functools
import json
import logging
import os
import sys
import time

import pkg_resources

from turberfield.ipc import __version__
from turberfield.ipc.cli import add_common_options
from turberfield.ipc.flow import Flow
from turberfield.ipc.fsdb import token
from turberfield.ipc.fsdb import Resource

APP_NAME = "turberfield.ipc.demo.sender"

class EchoClientProtocol:
    def __init__(self, queue, loop):
        self.queue = queue
        self.loop = loop
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        print("Received:", data.decode())

        print("Close the socket")
        self.transport.close()

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Socket closed, stop the event loop")
        loop = asyncio.get_event_loop()
        loop.stop()

    @asyncio.coroutine
    def __call__(self):
        while True:
            try:
                print("Waiting...")
                msg = yield from self.queue.get()
                # TODO: Framing
                print('Send:', msg)
                self.transport.sendto(msg.encode())
            except Exception as e:
                print(e)
                continue

__doc__ = """
Runs a '{0}' process.
""".format(APP_NAME)


def main(args):
    log = logging.getLogger(APP_NAME)
    log.setLevel(args.log_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s|%(message)s")
    ch = logging.StreamHandler()

    if args.log_path is None:
        ch.setLevel(args.log_level)
    else:
        fh = WatchedFileHandler(args.log_path)
        fh.setLevel(args.log_level)
        fh.setFormatter(formatter)
        log.addHandler(fh)
        ch.setLevel(logging.WARNING)

    ch.setFormatter(formatter)
    log.addHandler(ch)

    dif = token(args.connect, APP_NAME)
    flow = Flow.create(dif, poa="udp")
    log.info(flow)

    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)

    queue = asyncio.Queue(loop=loop)
    connect = loop.create_datagram_endpoint(
        lambda: EchoClientProtocol(queue, loop),
        remote_addr=('127.0.0.1', 9999))
    transport, protocol = loop.run_until_complete(connect)
    task = loop.create_task(protocol())
    loop.call_soon_threadsafe(functools.partial(queue.put_nowait, "Hello World!"))
    loop.run_forever()
    transport.close()
    loop.close()

def run():
    p = argparse.ArgumentParser(
        __doc__,
        fromfile_prefix_chars="@"
    )
    p = add_common_options(p)
    args = p.parse_args()
    if args.version:
        sys.stderr.write(__version__ + "\n")
        rv = 0
    else:
        rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
