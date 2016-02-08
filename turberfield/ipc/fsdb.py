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

from collections import defaultdict
from collections import namedtuple
import getpass
import itertools
import json
import operator
import os
import os.path
import pathlib
import platform
import tempfile
import urllib.parse
import warnings

from turberfield.ipc.flow import Flow
from turberfield.ipc.flow import Pooled
from turberfield.utils.misc import gather_installed


Resource = namedtuple(
    "Resource",
    ["root", "namespace", "user", "service", "application", "flow", "policy", "suffix"]
)

def recent_slot(path):
    slots = [i for i in os.listdir(os.path.join(path.root, path.home))
             if os.path.isdir(os.path.join(path.root, path.home, i))]
    stats = [(os.path.getmtime(os.path.join(path.root, path.home, fP)), fP)
             for fP in slots]
    stats.sort(key=operator.itemgetter(0), reverse=True)
    return Resource(
        path.root, path.home, next((i[1] for i in stats), None), path.file)

def references_by_policy(items):
    return defaultdict(list,
        {k: list(v) for k, v in itertools.groupby(items, key=operator.attrgetter("policy"))}
    )

def token(connect:str, serviceName:str, appName:str, userName:str=""):
    """
    Generates a token for use with the IPC framework.

    :param connect: A connection string in the form of a URL.
                    Just now this must be a file path to a user-writeable directory, eg:
                    'file:///home/alice/.turberfield'.
    :param serviceName: The name of a network of services.
    :param appName: The name of your application.

    """
    bits = urllib.parse.urlparse(connect)
    if bits.scheme != "file":
        warnings.warn("Only a file-based DIF cache is available")
        return None

    path = pathlib.Path(bits.netloc, bits.path)
    if platform.system() == "Windows":
        root = str(path).lstrip(path.root)
    else:
        root = str(path)

    user = userName or getpass.getuser()
    rv = Resource(
        root=root,
        namespace="turberfield",
        user=user,
        service=serviceName,
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
def create_from_resource(path:Resource, poa:list, role:list, routing:list, prefix="flow_", suffix=""):
    if all(path[:5]) and not any(path[5:]):
        parent = os.path.join(*path[:5])
        drctry = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=parent)
        flow = path._replace(flow=os.path.basename(drctry))

    # MRO important here.
    for registry, choices in [
        ("turberfield.ipc.routing", routing),
        ("turberfield.ipc.poa", poa),
        ("turberfield.ipc.role", role)
    ]:
        policies = dict(gather_installed(registry))
        for option in choices:
            try:
                typ = policies[option]
 
                if issubclass(typ, Pooled):
                    others = [Flow.inspect(i) for i in Flow.find(path, application="*", policy=option)]
                    obj = typ.allocate(others=others)
                else:
                    obj = typ()
                flow = flow._replace(policy=option, suffix=".json")
                with open(os.path.join(*flow[:-1]) + flow.suffix, 'w') as record:
                    record.write(obj.__json__())
                    record.flush()

            except KeyError:
                warnings.warn("No policy found for '{}'.".format(option))
                yield None
            except Exception as e:
                warnings.warn("Create error: {}".format(e))
                yield None
            else:
                yield flow

@Flow.find.register(Resource)
def find_by_resource(context:Resource, application=None, policy=None):
    query = Resource(
        context.root,
        context.namespace,
        context.user,
        context.service,
        application or context.application,
        context.flow or "*",
        policy or context.policy or "*",
        context.suffix or ".json"
    )
    if application in (None, "*"):
        p = pathlib.Path(*(i for i in query[0:4]))
        glob = p.glob(os.path.join("*", query.flow, query.policy + query.suffix))
    else:
        p = pathlib.Path(*query[0:5])
        glob = p.glob(os.path.join(query.flow, query.policy + query.suffix))
    return (r for t, r in sorted((
        (i.stat().st_mtime_ns, Resource(
            context.root,
            context.namespace,
            context.user,
            context.service,
            *i.parts[-3:-1],
            os.path.splitext(i.name)[0],
            suffix=i.suffix)
        )
        for i in glob),
        reverse=True)
    )

@Flow.inspect.register(Resource)
def inspect_by_resource(context:Resource):
    factories = {
        **dict(gather_installed("turberfield.ipc.poa")),
        **dict(gather_installed("turberfield.ipc.role")),
        **dict(gather_installed("turberfield.ipc.routing")),
    }
    with open(os.path.join(*context[:-1]) + context.suffix, 'r') as record:
        try:
            typ = factories[context.policy]
            obj = typ.from_json(record.read())
        except (AttributeError, KeyError) as e:
            return None
        else:
            return obj

@Flow.replace.register(Resource)
def replace_by_resource(path:Resource, obj):
    with open(os.path.join(*path[:-1]) + path.suffix, 'w') as record:
        record.write(obj.__json__())
