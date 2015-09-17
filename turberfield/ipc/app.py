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

import argparse
import asyncio
from collections import OrderedDict
import concurrent.futures
import json
import logging
import os
import sys
import time

import bottle
from bottle import Bottle
import pkg_resources

from turberfield.utils.expert import TypesEncoder

from addisonarches import __version__
from addisonarches.cli import add_common_options
from addisonarches.cli import add_web_options
import addisonarches.game
from addisonarches.utils import send

__doc__ = """
Runs the web interface for Turberfield.
"""


bottle.TEMPLATE_PATH.append(
    pkg_resources.resource_filename("addisonarches.web", "templates")
)

app = Bottle()

def authenticated_userid(request):
    return "someone@somewhere.net"

@app.route("/", "GET")
def home_get():
    log = logging.getLogger("addisonarches.web.home")
    userId = authenticated_userid(bottle.request)
    log.info(userId)
    args = app.config.get("args")
    send(args)
    path = os.path.join(
        app.config["args"].output, "player.rson"
    )
    ts = time.time()
    actor = None
    page = {
        "info": {
            "actor": actor,
            "interval": 200,
            "refresh": None,
            "time": "{:.1f}".format(ts),
            "title": "Turberfield {}".format(__version__),
            "version": __version__
        },
        "nav": [],
        "items": [],
        "options": [],
    }
    try:
        pass
    except Exception as e:
        log.exception(e)
    finally:
        return json.dumps(
            page, cls=TypesEncoder, indent=4
        )

@app.route("/titles", "GET")
@bottle.view("titles")
def titles_get():
    log = logging.getLogger("addisonarches.web.titles")

    items = []
    return {
        "info": {
            "args": app.config.get("args"),
            "debug": bottle.debug,
            "interval": 200,
            "time": "{:.1f}".format(time.time()),
            "title": "Turberfield {}".format(__version__),
            "version": __version__
        },
        "items": OrderedDict([(str(id(i)), i) for i in items]),
        
    }

@app.route("/audio/<filepath:path>")
def serve_audio(filepath):
    log = logging.getLogger("addisonarches.web.serve_audio")
    log.debug(filepath)
    locn = pkg_resources.resource_filename(
        "addisonarches.web", "static/audio"
    )
    return bottle.static_file(filepath, root=locn)


@app.route("/css/<filepath:path>")
def serve_css(filepath):
    log = logging.getLogger("addisonarches.web.serve_css")
    log.debug(filepath)
    locn = pkg_resources.resource_filename(
        "addisonarches.web", "static/css"
    )
    return bottle.static_file(filepath, root=locn)


@app.route("/data/<filename>")
def serve_data(filename):
    bottle.request.environ["HTTP_IF_MODIFIED_SINCE"] = None
    locn = app.config["args"].output
    response = bottle.static_file(filename, root=locn)
    response.expires = os.path.getmtime(locn)
    response.set_header("Cache-control", "max-age=0")
    return response


@app.route("/img/<filepath:path>")
def serve_img(filepath):
    log = logging.getLogger("addisonarches.web.serve_img")
    log.debug(filepath)
    locn = pkg_resources.resource_filename(
        "addisonarches.web", "static/img"
    )
    return bottle.static_file(filepath, root=locn)


@app.route("/js/<filepath:path>")
def serve_js(filepath):
    log = logging.getLogger("addisonarches.web.serve_js")
    log.debug(filepath)
    locn = pkg_resources.resource_filename(
        "addisonarches.web", "static/js"
    )
    return bottle.static_file(filepath, root=locn)


def main(args):
    log = logging.getLogger("addisonarches.web")
    log.setLevel(args.log_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s|%(message)s")
    ch = logging.StreamHandler()

    if args.log_path is None:
        ch.setLevel(args.log_level)
    else:
        fh = WatchedFileHandler(args.log_path)
        fh.setLevel(args.log_level)
        fh.setFormatter(formatter)
        log.addHandler(fh)
        ch.setLevel(logging.WARNING)

    ch.setFormatter(formatter)
    log.addHandler(ch)

    bottle.debug(True)
    bottle.TEMPLATES.clear()
    log.debug(bottle.TEMPLATE_PATH)

    log.info("Starting local server...")
    app.config.update({
        "args": args,
    })
    bottle.run(app, host=args.host, port=args.port)


def run():
    p = argparse.ArgumentParser(
        __doc__,
        fromfile_prefix_chars="@"
    )
    p = add_common_options(p)
    p = add_web_options(p)
    args = p.parse_args()
    if args.version:
        sys.stderr.write(__version__ + "\n")
        rv = 0
    else:
        rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
