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

from turberfield.utils.assembly import Assembly

Address = namedtuple(
    "Address",
    ["namespace", "user", "service", "application"]
)
Address.__doc__ = """`{}`

A semantically hierarchical address for distributed networking.

    namespace
        Specifies the domain within which the address names are valid.
    user
        A unique name of trust within the network.
    service
        Identifies a currently operating instantiation of the network.
    application
        The name of the node endpoint.

""".format(Address.__doc__)

Assembly.register(Address)
