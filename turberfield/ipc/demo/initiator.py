#!/usr/bin/env python
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
import os
import signal
import sys
import uuid

import aiohttp.web

from turberfield.ipc import __version__
from turberfield.ipc.cli import add_async_options
from turberfield.ipc.cli import add_common_options
from turberfield.ipc.cli import add_proactor_options
from turberfield.utils.misc import config_parser
from turberfield.utils.misc import log_setup

__doc__ = """

~/py3.5/bin/python -m turberfield.ipc.demo.initiator \\
--uuid={0.hex} --port=8080 \\
--config=turberfield/ipc/demo/proactor.cfg

""".format(uuid.uuid4())

def create_processor(guid, port):
    args = [
        sys.executable,
        "-m", "turberfield.ipc.demo.initiator",
        "--uuid", guid,
        "--port", port,
    ]
    log.info("Job: {0}".format(args))
    try:
        worker = subprocess.Popen(
            args,
            #cwd=app.config.get("args")["output"],
            shell=False
        )
    except OSError as e:
        log.error(e)
    else:
        log.info("Launched worker {0.pid}".format(worker))

def main(args):
    rv = 0
    loop = asyncio.get_event_loop()
    log = logging.getLogger(log_setup(args, loop=loop))
    log.info("Reading config...")
    cfg = config_parser()

    try:
        loop.run_until_complete(
            asyncio.wait_for(
                loop.run_in_executor(None, cfg.read_file, args.config),
                timeout=3
            )
        )
    except asyncio.TimeoutError:
        log.error("Timed out while reading config.")
        loop.stop()
        loop.close()
        os._exit(1)
    else:
        app = aiohttp.web.Application()
        handler = app.make_handler()
        f = loop.create_server(handler, "0.0.0.0", args.port)
        srv = loop.run_until_complete(f)
        log.info("Serving on {0}:{1}".format(*srv.sockets[0].getsockname()))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            srv.close()
            loop.run_until_complete(srv.wait_closed())
            loop.run_until_complete(app.shutdown())
            loop.run_until_complete(handler.shutdown(60.0))
            loop.run_until_complete(app.cleanup())
        loop.close()

    return rv

def run():
    p = add_common_options(
        add_async_options(
            add_proactor_options(
                argparse.ArgumentParser(
                    __doc__,
                    fromfile_prefix_chars="@"
                )
            )
        )
    )
    args = p.parse_args()
    if args.version:
        sys.stderr.write(__version__ + "\n")
        rv = 0
    else:
        rv = main(args)
    sys.exit(0)

if __name__ == "__main__":
    run()
