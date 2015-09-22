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
import operator
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

def token(connect:str, appName:str):
    bits = urllib.parse.urlparse(connect)
    if bits.scheme != "file":
        warnings.warn("Only a file-based POA cache is available")
        return None

    path = pathlib.Path(bits.netloc)
    user = getpass.getuser()
    rv = Resource(
        root=str(path).lstrip(path.root),
        namespace="turberfield",
        user=user,
        service="demo",
        application=appName,
        flow=None,
        policy=None,
        suffix=None
    )
    if appName is not None:
        session = os.path.join(*rv[:5])
        os.makedirs(session, exist_ok=True)

    return rv

@Flow.create.register(Resource)
def create_from_resource(path:Resource, policy, prefix="flow_", suffix=""):
    if all(path[:5]) and not any(path[5:]):
        parent = os.path.join(*path[:5])
        flow = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=parent)
        return path._replace(flow=os.path.basename(flow))
    else:
        return path

@Flow.find.register(Resource)
def find_by_resource(context:Resource, application=None, policy=None, role=None):
    scan = os.scandir(os.path.join(*[i for i in context if i is not None]))
    latest = sorted(scan, key=operator.methodcaller("stat"))
    return list(scan)
