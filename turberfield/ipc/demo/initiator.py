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
import os.path
try:
    from os import PathLike
except ImportError:
    PathLike = object
import pathlib
import sys

import aiohttp.web
from multidict import MultiDict

from turberfield.ipc import __version__
from turberfield.ipc.cli import add_async_options
from turberfield.ipc.cli import add_common_options
from turberfield.ipc.cli import add_proactor_options
import turberfield.ipc.demo.initiator
from turberfield.ipc.proactor import Initiator
from turberfield.utils.misc import config_parser
from turberfield.utils.misc import log_setup

__doc__ = """

~/py3.5/bin/python -m turberfield.ipc.demo.initiator \\
--uuid=8d740c16d9b8419aa7417f7da6deb039 --port=8080 \\
--config=turberfield/ipc/demo/proactor.cfg

"""


class LogPath(PathLike):

    def __fspath__(self):
        return "."

class Service:

    def __init__(self, *args, **kwargs):
        self.proactor = next(
            (i for i in args if isinstance(i, Initiator)),
            None
        )

    def setup_routes(self, app):
        app.router.add_get("/config", self.config)
        app.router.add_get("/task", self.task)
        app.router.add_get("/task/{task}", self.task)
        app.router.add_post("/create", self.create)

    async def config(self, request):
        cfg = self.proactor.cfg
        rv = {s: dict(cfg.items(s)) for s in cfg.sections()}
        return aiohttp.web.json_response(rv)

    async def create(self, request):
        data = await request.post()
        guid = await self.proactor.launch(turberfield.ipc.demo.initiator)
        root = ""  # Absolute host path
        rv = aiohttp.web.HTTPCreated(
            headers=MultiDict({"Refresh": "0;url={0}/task".format(root)})
        )
        return rv

    async def task(self, request):
        task = request.match_info.get("task")
        rv = self.proactor.tasks.get(task, self.proactor.tasks)
        return aiohttp.web.json_response(str(rv))

def main(args):
    rv = 0
    loop = asyncio.get_event_loop()
    log = logging.getLogger(log_setup(args, loop=loop))

    log.info("Place defaults")
    home = pathlib.Path(
        os.path.abspath(
            os.path.expanduser(
                os.path.join("~", ".turberfield")
            )
        )
    )
    home.mkdir(parents=True, exist_ok=True)
    initiator = Initiator(args, loop=loop)

    # TODO: Put in Processor as class method
    log.info("Read config...")
    try:
        initiator.read_config(args.config)
    except asyncio.TimeoutError:
        log.error("Time out while reading config.")
        loop.stop()
        loop.close()
        os._exit(1)
    else:
        app = aiohttp.web.Application()
        service = Service(initiator)
        service.setup_routes(app)
        handler = app.make_handler()
        addr = initiator.cfg.get(args.uuid, "listen_addr", fallback="0.0.0.0")
        port = initiator.cfg.getint(args.uuid, "listen_port", fallback=args.port)
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
