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

from turberfield.ipc.netstrings import dumpb
from turberfield.ipc.netstrings import loadb


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

    def test_dumpb_empty_message(self):
        """
        The empty string is encoded as "0:,".

        """
        packet = dumpb("")
        self.assertEqual(bytes([0x30, 0x3a, 0x2c]), packet)

    def test_dumpb_full_message(self):
        """
        The string "hello world!" is encoded as <31 32 3a 68
        65 6c 6c 6f 20 77 6f 72 6c 64 21 2c>, i.e., "12:hello world!,".
        """
        packet = dumpb("hello world!")
        self.assertEqual(bytes([
            0x31, 0x32,
            0x3a,
            0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x20, 0x77, 0x6f, 0x72, 0x6c, 0x64, 0x21,
            0x2c
        ]), packet)

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

    def test_loadb_message_tailnoise(self):
        """

        """
        packet = bytes([
            0x30,
            0x3a,
            0x2c,
            0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x20, 0x77, 0x6f, 0x72, 0x6c, 0x64, 0x21,
        ])
        decoder = loadb()
        msg = decoder.send(None)
        self.assertIs(None, msg)

        msg = decoder.send(packet)
        self.assertEqual("", msg)

    def test_loadb_badmessage(self):
        packet = bytes([
            0x30,
            0x3a,
            0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x20, 0x77, 0x6f, 0x72, 0x6c, 0x64, 0x21,
            0x2c,
        ])
        decoder = loadb()
        msg = decoder.send(None)
        self.assertIs(None, msg)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            msg = decoder.send(packet)
            self.assertIs(None, msg)
            self.assertTrue(
                issubclass(w[-1].category, UserWarning))
            self.assertIn("Framing error", str(w[-1].message))

        msg = decoder.send(bytes([0x30, 0x3a, 0x2c]))
        self.assertEqual("", msg)

    def test_loadb_full_message(self):
        """
        The string "hello world!" is encoded as <31 32 3a 68
        65 6c 6c 6f 20 77 6f 72 6c 64 21 2c>, i.e., "12:hello world!,".
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

    def test_loadb_bytewise_message(self):
        """
        The string "hello world!" is encoded as <31 32 3a 68
        65 6c 6c 6f 20 77 6f 72 6c 64 21 2c>, i.e., "12:hello world!,".
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

        for symbol in packet:
            msg = decoder.send([symbol])
        self.assertEqual("hello world!", msg)
