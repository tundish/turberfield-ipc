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
import logging
from logging.handlers import WatchedFileHandler
import sys

from turberfield.ipc import __version__
from turberfield.ipc.cli import add_common_options
from turberfield.ipc.cli import add_ipc_options
from turberfield.ipc.fsdb import token
from turberfield.ipc.node import create_udp_node

APP_NAME = "turberfield.ipc.demo.router"

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

    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)

    down = asyncio.Queue(loop=loop)
    up = asyncio.Queue(loop=loop)

    tok = token(args.connect, APP_NAME)
    node = create_udp_node(loop, tok, down, up)
    loop.create_task(node(token=tok))

    log.info("Starting router node...")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        for task in asyncio.Task.all_tasks(loop=loop):
            task.cancel()

        for resource in resources:
            resource.close()

    finally:
        loop.close()

def run():
    p = argparse.ArgumentParser(
        __doc__,
        fromfile_prefix_chars="@"
    )
    p = add_common_options(p)
    p = add_ipc_options(p)
    args = p.parse_args()
    if args.version:
        sys.stderr.write(__version__ + "\n")
        rv = 0
    else:
        rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
