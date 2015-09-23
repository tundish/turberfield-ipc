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

import unittest

__doc__ = """
_netstring definition: http://cr.yp.to/proto/netstrings.txt
"""

def loadb(encoding="utf-8"):
    buf = bytearray()
    span = None
    while span is None:
        data = yield None
        buf.extend(data)
        index = buf.find(b":")

        if index != -1:
            span = int(buf[0:index].decode("ascii"))
            del buf[0:index + 1]

    while span > len(buf):
        data = yield None
        buf.extend(data)
    else:
        if buf[span] != 44: #  b':'
            warnings.warn("Framing error.")
        else:
            rv = buf[0:span].decode(encoding=encoding)
            del buf[0:span + 1]
            yield rv

        span = None
        
    
        

class NetstringTests(unittest.TestCase):

    def test_raw(self):
        """
        <68 65 6c 6c 6f 20 77 6f 72 6c 64 21> is a string of length 12.
        It is the same as the string "hello world!
        """
        raw = bytes(
            [0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x20, 0x77, 0x6f, 0x72, 0x6c, 0x64, 0x21])
        self.assertEqual(12, len(raw))
        self.assertEqual("hello world!", raw.decode("ascii"))

    def test_dumpb(self):
        """
        <68 65 6c 6c 6f 20 77 6f 72 6c 64 21> is a string of length 12.
        It is the same as the string "hello world!
        """
        raw = bytes(
            [0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x20, 0x77, 0x6f, 0x72, 0x6c, 0x64, 0x21])
        self.assertEqual("hello world!", raw.decode("ascii"))

    def test_loadb_empty_message(self):
        """
        The empty string is encoded as "0:,".

        """
        packet = bytes([
            0x30,
            0x3a,
            0x2c
        ])
        decoder = loadb()
        msg = decoder.send(None)
        self.assertIs(None, msg)

        msg = decoder.send(packet)
        self.assertEqual("", msg)

    def test_loadb_message_headnoise(self):
        """

        """
        packet = bytes([
            0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x20, 0x77, 0x6f, 0x72, 0x6c, 0x64, 0x21,
            0x30,
            0x3a,
            0x2c
        ])
        decoder = loadb()
        msg = decoder.send(None)
        self.assertIs(None, msg)

        msg = decoder.send(packet)
        self.assertEqual("", msg)

    def test_loadb_full_message(self):
        """
        Any string of 8-bit bytes may be encoded as [len]":"[string]",".
        Here [string] is the string and [len] is a nonempty sequence of ASCII
        digits giving the length of [string] in decimal. The ASCII digits are
        <30> for 0, <31> for 1, and so on up through <39> for 9. Extra zeros
        at the front of [len] are prohibited: [len] begins with <30> exactly
        when [string] is empty.

        For example, the string "hello world!" is encoded as <31 32 3a 68
        65 6c 6c 6f 20 77 6f 72 6c 64 21 2c>, i.e., "12:hello world!,". The
        empty string is encoded as "0:,".
        """
        packet = bytes([
            0x31, 0x32,
            0x3a,
            0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x20, 0x77, 0x6f, 0x72, 0x6c, 0x64, 0x21,
            0x2c
        ])
        decoder = loadb()
        msg = decoder.send(None)
        self.assertIs(None, msg)

        msg = decoder.send(packet)
        self.assertEqual("hello world!", msg)
