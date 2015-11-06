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


from functools import singledispatch
import warnings

class Pooled:

    @classmethod
    def allocate(cls, others=[]):
        raise NotImplementedError

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
        warnings.warn("No inspect function registered for {}".format(type(obj)))
        return None

    @staticmethod
    @singledispatch
    def replace(obj, data, *args, **kwargs):
        warnings.warn("No replace function registered for {}".format(type(obj)))
        return None
