import asyncio
from collections import namedtuple
from collections import OrderedDict
import configparser
import io
import itertools
import logging
import multiprocessing
import subprocess
import sys
import textwrap
import uuid

from turberfield.utils.misc import config_parser
from turberfield.utils.misc import clone_config_section
from turberfield.utils.misc import reference_config_section


class Proactor:

    CONFIG_TIMEOUT_SEC = 3

    def __init__(self, options, loop=None, **kwargs):
        self.args = options
        self.loop = loop or asyncio.get_event_loop()
        self.cfg = config_parser(**kwargs)

    def read_config(self, fObj):
        self.loop.run_until_complete(
            asyncio.wait_for(
                self.loop.run_in_executor(
                    None, self.cfg.read_file, fObj
                ),
                timeout=self.CONFIG_TIMEOUT_SEC
            )
        )

    def register_connection(self, guid, port=None):
        addr = self.cfg.get(guid, "listen_addr", fallback="0.0.0.0")
        port = port or self.cfg.getint(guid, "listen_port")
        self.cfg[guid]["listen_port"] = str(port)
        return addr, port

class Initiator(Proactor):

    Worker = namedtuple(
        "Worker",
        ["guid", "port", "session", "module", "process"]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = asyncio.Queue(loop=self.loop)
        self.tasks = OrderedDict([])
        self.loop.create_task(self.task_runner())
        self.log = logging.getLogger("turberfield.ipc.proactor.initiator")

    @staticmethod
    def next_port(cfg, guid):
        pool = range(
            cfg.getint(guid, "child_port_min"),
            cfg.getint(guid, "child_port_max") + 1
        )
        taken = {cfg.getint(s, "listen_port", fallback=None) for s in cfg.sections()}
        return next(iter(sorted(set(pool).difference(taken))), None)

    async def task_runner(self):
        self.log.info("Running tasks")
        try:
            while True:
                guid = await self.queue.get()
                task = self.tasks.get(guid)
                if task:
                    self.tasks[guid] = await task
                    self.log.info(self.tasks[guid])
                    # TODO: remove section from cfg if no port allocated
        except asyncio.CancelledError:
            pass

    async def worker(self, module, guid, interpreter=sys.executable):
        port = self.next_port(self.cfg, self.args.guid)
        section = "\n".join(itertools.chain(
            clone_config_section(self.cfg, module.__name__, guid, listen_port=port),
            reference_config_section(
                self.cfg, self.args.guid, parent_addr="listen_addr", parent_port="listen_port"
            ),
        ))
        self.cfg.read_string(section)

        args = [
            interpreter,
            "-m", module.__name__,
            "--guid", guid,
            "--port", str(port),
        ]
        proc = await asyncio.create_subprocess_exec(
          *args, stdin=subprocess.PIPE, loop=self.loop
        )

        data = io.StringIO()
        self.cfg.write(data)
        proc.stdin.write(data.getvalue().encode("utf-8"))
        await proc.stdin.drain()
        proc.stdin.close()

        task = asyncio.wait_for(
            proc.wait(),
            timeout=self.CONFIG_TIMEOUT_SEC + 2
        )
        try:
            await task
        except asyncio.TimeoutError:
            return self.Worker(guid, port, None, module, proc)
        else:
            return self.Worker(guid, None, None, module, proc)

    async def launch(self, module, guid=None):
        guid = guid or uuid.uuid4().hex
        self.tasks[guid] = self.worker(module, guid)
        await self.queue.put(guid)
        return guid
