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


class POA:
    """
        Advertised through turberfield.ipc.poa entry point.

    """
    UDP = namedtuple("UDP", ["port"])

class Role:
    """
        Advertised through turberfield.ipc.role entry point.

    """
    RX = namedtuple("RX", ["tMaxPdu", "tMaxAck", "tMaxRtx"])
    TX = namedtuple("TX", ["tMaxPdu", "tMaxAck", "tMaxRtx"])
