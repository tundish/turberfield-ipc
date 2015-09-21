#!/usr/bin/env python3
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

from collections import namedtuple
import getpass
import os.path
import pathlib
import tempfile
import urllib.parse
import warnings

from turberfield.ipc.flow import Flow

Resource = namedtuple(
    "Resource",
    ["root", "namespace", "user", "service", "application", "flow", "policy", "suffix"]
)

def token(connect, appName):
    bits = urllib.parse.urlparse(connect)
    if bits.scheme != "file":
        warnings.warn("Only a file-based POA cache is available")
        return None

    print(bits)
    path = pathlib.Path(bits.path)
    user = getpass.getuser()
    return Resource(str(path).lstrip(path.root), "turberfield", user, "demo", appName, None, None, None)

@Flow.create.register(Resource)
def create_from_resource(path:Resource, prefix="flow_", suffix=""):
    if all(path[:4]) and not any(path[5:]):
            parent = os.path.join(*path[:5])
            os.makedirs(parent, exist_ok=True)
            flow = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=parent)
            return path._replace(flow=os.path.basename(flow))
    else:
        return path


def get_DIF(connect):
    bits = urllib.parse.urlparse(connect)
    if bits.scheme != "file":
        warnings.warn("Only a file-based POA cache is available")
        return None

    path = pathlib.Path(bits.path)
    user = getpass.getuser()
    return Resource(path, "turberfield", user, "demo", APP_NAME, None, None, None)
