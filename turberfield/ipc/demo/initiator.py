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
import signal
import sys

from turberfield.ipc import __version__
from turberfield.ipc.cli import add_async_options
from turberfield.ipc.cli import add_common_options
from turberfield.ipc.cli import add_config_options
from turberfield.utils.misc import config_parser
from turberfield.utils.misc import log_setup

"""
Prototype initiator.

"""

def main(args):
    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)

    log = logging.getLogger(log_setup(args, loop=loop))
    log.info("Reading config...")
    cfg = config_parser()
    cfg.read_file(args.config)
    print(cfg)
    return 0

def run():
    p = add_common_options(
        add_async_options(
            add_config_options(
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
