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

import warnings


__doc__ = """
.. _netstring definition: http://cr.yp.to/proto/netstrings.txt
"""

def dumpb(data, encoding="utf-8"):
    payload = data.encode(encoding=encoding)
    return b"%d:%b," % (len(payload), payload)

def loadb(encoding="utf-8"):
    buf = bytearray()
    span = None
    rv = None
    while True:
        while span is None:
            colon = buf.find(b":")

            if colon != -1:
                # work backwards from colon over length field
                index = colon - 1
                while index >= 0 and 0x30 <= buf[index] <= 0x39:
                    index -= 1

                span = int(buf[index + 1:colon].decode("ascii"))
                del buf[0:colon + 1]
            else:
                data = yield rv
                buf.extend(data)

        while len(buf) < span + 1:
            data = yield None
            buf.extend(data)
        else:
            if buf[span] != 44: #  b','
                warnings.warn("Framing error.")
                rv = None
            else:
                rv = buf[0:span].decode(encoding=encoding)
                del buf[0:span + 1]

            span = None
