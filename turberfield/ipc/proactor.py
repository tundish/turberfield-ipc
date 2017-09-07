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

class Processor(Proactor):
    pass

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

    async def task_runner(self):
        self.log.info("Running tasks")
        try:
            while True:
                guid = await self.queue.get()
                task = self.tasks.get(guid)
                if task:
                    rv = await task
                    self.log.info(rv)
        except asyncio.CancelledError:
            pass

    async def worker(self, module, guid, interpreter=sys.executable):
        port = self.cfg.getint("default", "port", fallback=8081)
        args = [
            interpreter,
            "-m", module.__name__,
            "--guid", guid,
            "--port", str(port),
            #"--log", os.path.join(root, session, progress.slot, "run.log")
        ]
        proc = await asyncio.create_subprocess_exec(
          *args, stdin=subprocess.PIPE, loop=self.loop
        )
        section = "\n".join(itertools.chain(
            clone_config_section(self.cfg, module.__name__, guid, listen_port=port),
        ))
        self.cfg.read_string(section)

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
            return self.Worker(guid, port, None, None, proc)
        else:
            return self.Worker(guid, None, None, None, proc)

    async def launch(self, module, guid=None):
        guid = guid or uuid.uuid4().hex
        self.tasks[guid] = self.worker(module, guid)
        await self.queue.put(guid)
        return guid
