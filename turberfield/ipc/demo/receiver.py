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
from collections import defaultdict
import logging
import sys

from turberfield.ipc import __version__
from turberfield.ipc.cli import add_common_options
from turberfield.ipc.flow import Flow
from turberfield.ipc.fsdb import token

APP_NAME = "turberfield.ipc.demo.receiver"

class EchoServerProtocol:

    def __init__(self, queue, loop):
        self.queue = queue
        self.loop = loop
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
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

    tok = token(args.connect, APP_NAME)
    services = defaultdict(list)
    for i in Flow.create(tok, poa=["udp"], role=[], routing=[]):
        policy = Flow.inspect(i)
        services[policy.mechanism].append(policy)

    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)

    down = asyncio.Queue(loop=loop)
    up = asyncio.Queue(loop=loop)
    for mech, policies in services.items():
        log.info("{0} {1}".format(mech, [vars(i) for i in policies]))
        launcher = mech.launcher(loop, policies, down, up)
        transport, protocol = loop.run_until_complete(launcher)
        loop.create_task(protocol(token=tok))
        
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    #transport.close()
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
