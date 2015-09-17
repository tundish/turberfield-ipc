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
from collections import namedtuple
import locale
import logging
import os
import sys

def subprocess_queue_factory(queue, loop):

    def pipe_data_received(self, fd, data):
        if fd == 1:
            name = 'stdout'
        elif fd == 2:
            name = 'stderr'
        text = data.decode(locale.getpreferredencoding(False))
        print('Received from {}: {}'.format(name, text.strip()))

    def connection_lost(self, exc):
        self.loop.stop() # end loop.run_forever()

    def process_exited(self):
        self.loop.stop()

    return type(
        "SubprocessQueue",
        (asyncio.SubprocessProtocol,),
        dict(
            loop=loop,
            connection_lost=connection_lost,
            pipe_data_received=pipe_data_received,
            process_exited=process_exited,
            queue=queue
        )
    )

def main(args):
    rv = 0
    if os.name == "nt":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    queue = asyncio.Queue(loop=loop)
    transport = loop.run_until_complete(
        loop.subprocess_exec(
            subprocess_queue_factory(queue, loop),
            sys.executable,
            "-m", "turberfield.ipc.app",
            *["--{}={}".format(i, getattr(args, i))
            for i in  ("output", "host", "port")] 
        )
    )[0]
    loop.run_forever()
    return rv


def run():
    p, subs = parsers()
    add_console_command_parser(subs)
    add_web_command_parser(subs)
    args = p.parse_args()

    rv = 0
    if args.version:
        sys.stdout.write(addisonarches.__version__ + "\n")
    else:
        rv = main(args)

    if rv == 2:
        sys.stderr.write("\n Missing command.\n\n")
        p.print_help()

    sys.exit(rv)

if __name__ == "__main__":
    run()
