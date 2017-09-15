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
        """
        This class provides the basic behaviour required for a module which
        performs a job of work.

        :param options: An `argparse.Namespace` or other object giving dotted-name
            attribute access to command line options.
        :param loop: An event loop compatible with `asyncio.AbstractEventLoop`.

        """
        self.args = options
        self.loop = loop or asyncio.get_event_loop()
        self.cfg = config_parser(**kwargs)
        self.tasks = []

    def read_config(self, fObj, timeout=CONFIG_TIMEOUT_SEC):
        """Read this object's configuration file from a file stream (eg: standard input).

        This method will raise `asyncio.TimeoutError` if the configuration
        is not seen within the timeout interval.

        It runs within this object's event loop. 

        :param fObj: A file stream object.
        :param timeout: A timeout interval in seconds.
        """
        self.loop.run_until_complete(
            asyncio.wait_for(
                self.loop.run_in_executor(
                    None, self.cfg.read_file, fObj
                ),
                timeout=timeout
            )
        )

    def register_connection(self, guid, port=None):
        addr = self.cfg.get(guid, "listen_addr", fallback="0.0.0.0")
        port = port or self.cfg.getint(guid, "listen_port")
        self.cfg[guid]["listen_port"] = str(port)
        return addr, port

class Initiator(Proactor):

    """
    The role of an Initiator is to launch executable modules as worker
    processes, or `jobs`. It is a subclass of
    :py:class:`Proactor <turberfield.ipc.proactor.Proactor>`.

    """

    Worker = namedtuple(
        "Worker",
        ["guid", "port", "session", "module", "process"]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = asyncio.Queue(loop=self.loop)
        self.jobs = OrderedDict([])
        self.tasks.append(self.loop.create_task(self.job_runner()))
        self.log = logging.getLogger("turberfield.ipc.proactor.initiator")
        self.busy = set([])

    @staticmethod
    def next_port(cfg, guid, busy=set([])):
        """Calculate a value for the next available port on this host.

        :param cfg: A `configparser.ConfigParser` object.
        :param guid: The global id for the Initiator which allocates ports.
        :param busy: A set of integer values; these are port numbers
            known to be busy.
        :rtype: integer
        """
        pool = range(
            cfg.getint(guid, "child_port_min"),
            cfg.getint(guid, "child_port_max") + 1
        )
        taken = busy.union(
            {cfg.getint(s, "listen_port", fallback=None) for s in cfg.sections()}
        )
        return next(iter(sorted(set(pool).difference(taken))), None)

    async def job_runner(self):
        self.log.info("Running jobs")
        try:
            while True:
                guid = await self.queue.get()
                job = self.jobs.get(guid)
                if job:
                    worker = await job
                    self.log.debug(worker)
                    if not worker.port:
                        self.cfg.remove_section(guid)
                        del self.jobs[guid]
                        await self.launch(worker.module, worker.guid)
                    else:
                        self.jobs[guid] = worker
        except asyncio.CancelledError:
            pass

    async def worker(self, module, guid, interpreter=sys.executable, **kwargs):
        port = self.next_port(self.cfg, self.args.guid, self.busy)
        section = "\n".join(itertools.chain(
            clone_config_section(self.cfg, module.__name__, guid, listen_port=port, **kwargs),
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

        job = asyncio.wait_for(
            proc.wait(),
            timeout=self.CONFIG_TIMEOUT_SEC + 2
        )
        try:
            await job
        except asyncio.TimeoutError:
            return self.Worker(guid, port, None, module, proc)
        else:
            self.busy.add(port)
            return self.Worker(guid, None, None, module, proc)

    async def launch(self, module, guid=None):
        """Schedule a job to be spawned in a worker process.

        This is a *coroutine*.

        :param module: A reference to a Python executable module.
            The module will be passed the following command line options:

            --guid
                The guid of the job.
            --port
                A TCP port for the job to bind to.

            The module must read its configuration from the standard input stream.
        :param guid: A unique id for the job. There is usually no need to
            supply this parameter. It will be generated internally.
        :returns: A guid to identify the new job.
        """
        guid = guid or uuid.uuid4().hex
        self.jobs[guid] = self.worker(module, guid)
        await self.queue.put(guid)
        return guid
