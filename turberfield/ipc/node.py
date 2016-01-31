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
import logging
import warnings

from turberfield.ipc.flow import Flow
from turberfield.utils.assembly import Assembly

__doc__ = """

.. py:function:: create_udp_node(loop, token, down, up, types)
   
   :param loop: An asyncio_ event loop.
   :param token: A DIF token.
   :param down: An asyncio_ queue which takes messages down to the network POA.
   :param up: An asyncio_ queue which bring up messages from the network POA.
   :param types: An optional dictionary of types mapped by their fully qualified names.
   :rtype: An asyncio_ Protocol instance.

.. _asyncio: https://docs.python.org/3/library/asyncio.html#module-asyncio

"""

Policy = namedtuple("Policy", ["routing", "poa", "role"])

class TakesPolicy:

    def __init__(self, *args, **kwargs):
        self.policy = Policy(*(kwargs.pop(i) for i in Policy._fields))
        super().__init__(*args, **kwargs)


def match_policy(token, policy:Policy):
    # MRO important here.
    policies = [i for p in policy for i in p]
    flows = Flow.find(token)
    for flow in flows:
        matched = []
        for p in policies:
            matched.append(next(Flow.find(token, application=token.application, policy=p), None))
        if all(matched):
            return matched
    return None

def create_udp_node(loop, token, down, up):
    """
    Creates a node which uses UDP for inter-application messaging

    """
    assert loop.__class__.__name__.endswith("SelectorEventLoop")
 
    services = []
    types = Assembly.register(Policy)
    policies = Policy(poa=["udp"], role=[], routing=["application"])
    refs = match_policy(token, policies) or Flow.create(token, **policies._asdict())
    for ref in refs:
        obj = Flow.inspect(ref)
        key = next(k for k, v in policies._asdict().items() if ref.policy in v) 
        field = getattr(policies, key)
        field[field.index(ref.policy)] = obj
        try:
            services.append(obj.mechanism)
        except AttributeError:
            warnings.warn("Policy '{}' lacks a mechanism".format(ref.policy))

    udp = next(iter(policies.poa))
    Mix = type("UdpNode", tuple(services), {})
    transport, protocol = loop.run_until_complete(
        loop.create_datagram_endpoint(
            lambda:Mix(loop, token, types, down=down, up=up, **policies._asdict()),
            local_addr=(udp.addr, udp.port)
        )
    )
    return protocol
