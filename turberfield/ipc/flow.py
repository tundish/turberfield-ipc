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
from functools import singledispatch
import os.path
import warnings

import pkg_resources

# TODO: resite
def gather_from_installation(key):
    for i in pkg_resources.iter_entry_points(key):
        try:
            ep = i.resolve()
        except Exception as e:
            continue
        else:
            yield (i.name, ep)

class Flow:

    @staticmethod
    @singledispatch
    def create(obj, *args, **kwargs):
        warnings.warn("No create function registered for {}".format(type(obj)))
        return None

    @staticmethod
    @singledispatch
    def find(query, *args, **kwargs):
        warnings.warn("No find function registered for {}".format(type(query)))
        return None

    @staticmethod
    @singledispatch
    def inspect(obj, *args, **kwargs):
        warnings.warn("No find function registered for {}".format(type(obj)))
        return None

def recent_slot(path):
    slots = [i for i in os.listdir(os.path.join(path.root, path.home))
             if os.path.isdir(os.path.join(path.root, path.home, i))]
    stats = [(os.path.getmtime(os.path.join(path.root, path.home, fP)), fP)
             for fP in slots]
    stats.sort(key=operator.itemgetter(0), reverse=True)
    return Persistent.Resource(
        path.root, path.home, next((i[1] for i in stats), None), path.file)
