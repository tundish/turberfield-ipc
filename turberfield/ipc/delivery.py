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

from turberfield.ipc.flow import Flow
from turberfield.ipc.message import Message
from turberfield.ipc.types import Address


class PeerRouter:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def hop(self, token, msg, policy):
        here = Address(
            token.namespace, token.user, token.service, token.application)

        if msg.header.hop >= msg.header.hMax:
            return (None, None)

        msg = Message(
            msg.header._replace(
                hop=msg.header.hop + 1,
                via=here
            ),
            msg.payload
        )

        if msg.header.dst == here:
            return (None, msg)
            
        hop = next(Flow.find(
            token,
            application=msg.header.dst.application,
            policy=policy),
        None)
        if hop is None:
            # TODO: Get next hop from routing table
            # mechanism
            #search = ((i, Flow.inspect(i)) for i in Flow.find(token, policy="application"))
            #query = (
            #    ref
            #    for ref, table in search
            #    for rule in table
            #    if rule.dst.application == msg.header.via.application
            #)
            return (None, msg)

        poa = Flow.inspect(hop)
        return (poa, msg)
