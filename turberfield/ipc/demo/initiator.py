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
from collections import OrderedDict
import logging
import os
import sys
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

class Initiator:

    @staticmethod
    def config(section):
        return {}

class Processor:

    @staticmethod
    def config(section):
        return {}

class Services:

    @classmethod
    def setup_routes(cls, app):
        app.router.add_get("/", cls.config)
        app.router.add_get("/task", cls.task)
        app.router.add_get("/task/{task}", cls.task)
        app.router.add_post("/create", cls.create)

    async def creator(app):
        print("Running")
        try:
            while True:
                job = await app.queue.get()
                print(job)
        except asyncio.CancelledError:
            pass

    @staticmethod
    async def start_background_tasks(app):
        app.tasks["creator"] = app.loop.create_task(Services.creator(app))
        print(app.tasks)

    @staticmethod
    async def cleanup_background_tasks(app):
        for task in app.tasks.values():
            task.cancel()
            await task

    async def config(request):
        cfg = request.app.cfg
        rv = {s: dict(cfg.items(s)) for s in request.app.cfg.sections()}
        return aiohttp.web.json_response(rv)

    async def create(request):
        data = await request.post()
        await request.app.queue.put(data)
        root = ""  # Absolute host path
        rv = aiohttp.web.HTTPCreated(
            headers=MultiDict({"Refresh": "0;url={0}/task".format(root)})
        )
        return rv

    async def task(request):
        task = request.match_info.get("task")
        rv = request.app.tasks.get(task, request.app.tasks)
        return aiohttp.web.json_response(rv)

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
        app.cfg = cfg
        app.tasks = OrderedDict([])
        app.queue = asyncio.Queue(loop=loop)
        #app.on_startup.append(Services.start_background_tasks)
        #app.on_cleanup.append(Services.cleanup_background_tasks)
        Services.setup_routes(app)
        handler = app.make_handler()
        f = loop.create_server(handler, "0.0.0.0", args.port)
        srv = loop.run_until_complete(f)
        log.info("Serving on {0}:{1}".format(*srv.sockets[0].getsockname()))
        try:
            #aiohttp.web.run_app(app)
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
