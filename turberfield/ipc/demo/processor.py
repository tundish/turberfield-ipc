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
import sys

import aiohttp.web

from turberfield.ipc import __version__
from turberfield.ipc.cli import add_async_options
from turberfield.ipc.cli import add_common_options
from turberfield.ipc.cli import add_proactor_options
from turberfield.ipc.proactor import Processor
from turberfield.utils.misc import log_setup


class Service:

    def __init__(self, proactor, **kwargs):
        self.proactor = proactor

    def setup_routes(self, app):
        app.router.add_get("/config", self.config)
        app.router.add_get("/task", self.task)
        app.router.add_get("/task/{task}", self.task)

    async def config(self, request):
        cfg = self.proactor.cfg
        rv = {s: dict(cfg.items(s)) for s in cfg.sections()}
        return aiohttp.web.json_response(rv)

    async def task(self, request):
        task = request.match_info.get("task")
        rv = self.proactor.tasks.get(task, self.proactor.tasks)
        return aiohttp.web.json_response(str(rv))


def main(args):
    rv = 0
    loop = asyncio.get_event_loop()
    logName = log_setup(args, loop=loop)
    log = logging.getLogger(logName + ".processor")

    processor = Processor(args, loop=loop)

    log.info("Read config...")
    try:
        processor.read_config(args.config)
    except asyncio.TimeoutError:
        log.error("Time out while reading config.")
        loop.stop()
        loop.close()
        os._exit(1)
    else:
        addr, port = processor.register_connection(args.guid, args.port)

        app = aiohttp.web.Application()
        service = Service(processor)
        service.setup_routes(app)
        handler = app.make_handler()

        f = loop.create_server(handler, addr, port)
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
