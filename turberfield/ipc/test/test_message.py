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


import textwrap
import unittest
import warnings

import turberfield.ipc.message


class MessageTester(unittest.TestCase):

    def test_loads_empty_payload(self):
        data = textwrap.dedent("""
        {
        _type: turberfield.ipc.message.Header,
        id: "aa27e84fa93843658bfcd5b4f9ceee4f",
        src: null,
        dst: null,
        hMax: 3,
        via: null,
        hop: 0
        }
        """)
        msg = turberfield.ipc.message.loads(data)
        self.assertIsInstance(msg, turberfield.ipc.message.Message)
        self.assertIsInstance(msg.header, turberfield.ipc.message.Header)
        self.assertIsInstance(msg.payload, list)
        self.assertFalse(msg.payload)

    def test_loads_bad_header(self):
        data = textwrap.dedent("""
        {
        _type: turberfield.ipc.message.Header,
        id: "aa27e84fa93843658bfcd5b4f9ceee4f",
        src: null,
        dst: null,
        hMax: 3,
        hop: 0
        }
        """)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            steps = list(turberfield.ipc.message.loads(data))
            self.assertEqual(1, len(w))
            self.assertTrue(
                issubclass(w[-1].category, UserWarning))
            self.assertIn("Parameter mismatch", str(w[-1].message))

    def test_loads_bogus_header(self):
        data = textwrap.dedent("""
        {
        _type: turberfield.ipc.message.Bogus,
        id: "aa27e84fa93843658bfcd5b4f9ceee4f",
        src: null,
        dst: null,
        hMax: 3,
        via: null,
        hop: 0
        }
        """)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            steps = list(turberfield.ipc.message.loads(data))
            self.assertEqual(2, len(w))
            self.assertTrue(
                issubclass(w[-1].category, UserWarning))
            self.assertIn("not recognised", str(w[0].message))
