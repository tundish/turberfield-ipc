#!/usr/bin/env python3
#   -*- encoding: UTF-8 -*-

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
import logging
import os.path
import pathlib
import sys

DFLT_LOCN = pathlib.PurePath(
        os.path.abspath(
            os.path.expanduser(
                os.path.join("~", ".turberfield")
            )
        )
    ).as_uri()
DFLT_PORT = 8080

def add_common_options(parser):
    parser.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number")
    parser.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
    parser.add_argument(
        "--log", default=None, dest="log_path",
        help="Set a file path for log output")
    return parser

def add_proactor_options(parser):
    parser.add_argument(
        "--config", nargs="?", default=sys.stdin, type=argparse.FileType("r"),
        help="Supply a configuration."
    )
    parser.add_argument(
        "--guid", required=True,
        help="Specify the guid of the processor"
    )
    parser.add_argument(
        "--port", type=int, required=False,
        help="Specify the port number to the processor"
    )
    return parser

def add_ipc_options(parser):
    parser.add_argument(
        "--connect", default=DFLT_LOCN,
        help="Connection string to IPC framework [{}]".format(DFLT_LOCN))
    return parser

def add_async_options(parser):
    parser.add_argument(
        "--debug", action="store_true", default=False,
        help="Print wire-level messages for debugging")
    return parser

def add_web_options(parser):
    parser.add_argument(
        "--host", default="localhost",
        help="Specify the name of the remote host")
    parser.add_argument(
        "--port", type=int, default=DFLT_PORT,
        help="Specify the port number [{}] to the host".format(DFLT_PORT))
    parser.add_argument(
        "--user", required=False,
        help="Specify the user login on the host")
    return parser
