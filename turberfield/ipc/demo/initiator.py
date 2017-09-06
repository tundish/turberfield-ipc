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
from collections import namedtuple
from collections import OrderedDict
import io
import logging
import os.path
try:
    from os import PathLike
except ImportError:
    PathLike = object
import pathlib
import subprocess
import sys
import textwrap
import uuid

import aiohttp.web
from multidict import MultiDict

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

CONFIG_TIMEOUT_SEC = 3


class LogPath(PathLike):

    def __fspath__(self):
        return "."

class Initiator:

    Worker = namedtuple(
        "Worker",
        ["guid", "port", "session", "module", "process"]
    )

    @staticmethod
    def config(section):
        return {}

    def __init__(self, cfg, loop=None):
        self.cfg = cfg
        self.loop = loop or asyncio.get_event_loop()
        self.queue = asyncio.Queue(loop=loop)
        self.tasks = OrderedDict([])
        self.loop.create_task(self.task_runner())

    async def task_runner(self):
        print("Running")
        try:
            while True:
                guid = await self.queue.get()
                print(guid)
                task = self.tasks.get(guid)
                print(task)
                if task:
                    rv = await task
                    print(rv)
        except asyncio.CancelledError:
            pass

    async def worker(self, guid=None, loop=None):
        log = logging.getLogger("")
        guid = guid or uuid.uuid4().hex
        port = self.cfg.getint("default", "port", fallback=8081)
        args = [
            sys.executable,
            "-m", "turberfield.ipc.demo.initiator",
            "--uuid", guid,
            "--port", str(port),
            #"--log", os.path.join(root, session, progress.slot, "run.log")
        ]
        proc = await asyncio.create_subprocess_exec(
          *args, stdin=subprocess.PIPE, loop=self.loop
        )
        self.cfg.read_string(textwrap.dedent(
        """
        [{guid}]
        a = 2
        """
        ).format(guid=guid))

        data = io.StringIO()
        self.cfg.write(data)
        proc.stdin.write(data.getvalue().encode("utf-8"))
        await proc.stdin.drain()
        proc.stdin.close()

        task = asyncio.wait_for(
            proc.wait(),
            timeout=CONFIG_TIMEOUT_SEC + 2
        )
        try:
            await task
        except asyncio.TimeoutError:
            return self.Worker(guid, port, None, None, proc)
        else:
            return self.Worker(guid, None, None, None, proc)


class Processor:

    @staticmethod
    def config(section):
        return {}

class Service:

    def __init__(self, *args, **kwargs):
        self.initiator = next(
            (i for i in args if isinstance(i, Initiator)),
            None
        )

    def setup_routes(self, app):
        app.router.add_get("/config", self.config)
        app.router.add_get("/task", self.task)
        app.router.add_get("/task/{task}", self.task)
        app.router.add_post("/create", self.create)

    async def config(self, request):
        cfg = self.initiator.cfg
        rv = {s: dict(cfg.items(s)) for s in cfg.sections()}
        return aiohttp.web.json_response(rv)

    async def create(self, request):
        data = await request.post()
        guid = uuid.uuid4().hex
        self.initiator.tasks[guid] = self.initiator.worker(guid=guid)
        await self.initiator.queue.put(guid)
        root = ""  # Absolute host path
        rv = aiohttp.web.HTTPCreated(
            headers=MultiDict({"Refresh": "0;url={0}/task".format(root)})
        )
        return rv

    async def task(self, request):
        task = request.match_info.get("task")
        rv = self.initiator.tasks.get(task, self.initiator.tasks)
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
    cfg = config_parser(home=str(home))

    # TODO: Put in Processor as class method
    log.info("Read config...")
    try:
        loop.run_until_complete(
            asyncio.wait_for(
                loop.run_in_executor(None, cfg.read_file, args.config),
                timeout=CONFIG_TIMEOUT_SEC
            )
        )
    except asyncio.TimeoutError:
        log.error("Time out while reading config.")
        loop.stop()
        loop.close()
        os._exit(1)
    else:
        app = aiohttp.web.Application()
        initiator = Initiator(cfg, loop=loop)
        service = Service(initiator)
        service.setup_routes(app)
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
