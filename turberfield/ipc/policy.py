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
import json
import random

from turberfield.ipc.flow import Flow

# TODO: resite
class SavesToJSON:

    @classmethod
    def from_json(cls, data):
        return cls(**json.loads(data))

    def __json__(self):
        return json.dumps(vars(self), indent=0, ensure_ascii=False, sort_keys=False)

class POA:
    """
        Advertised through turberfield.ipc.poa entry point.

    """
    class UDP(SavesToJSON):

        def __init__(self, port=None, pool=slice(49152, 65535), taken=[]):
            # TODO: Taken is a list of existing objects
            self.port = port or random.randint(pool.start, pool.stop)

class Role:
    """
        Advertised through turberfield.ipc.role entry point.

    """
    RX = namedtuple("RX", ["tMaxPdu", "tMaxAck", "tMaxRtx"])
    TX = namedtuple("TX", ["tMaxPdu", "tMaxAck", "tMaxRtx"])
