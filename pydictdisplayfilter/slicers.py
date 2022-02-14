# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of ipranger.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import ipaddress
from typing import Any, List

import pyparsing as pp

from pydictdisplayfilter.exceptions import ProgrammingError


class BasicSlicer:
    """
    A basic slicer which splits a value based on a slice specification.

    name == Neo
    name[0] == N
    name[0:2] == Ne
    name[:2] == Ne
    name[2:] == o
    name[1-2] == Ne
    name[0,1] == Ne,
    name[:2,2-3] == Neo

    """

    def __init__(self, specs, value: Any, separator_char: str= ''):
        """
        Initializes the BasicSlicer. This class is meant as basis for other slicers and does the heavy lifting.
        :param specs: the slice specification as list of lists of integers (e.g. [[0,1], [None, 2]]).
        :param value: the value to be sliced. Can be anything.
        :param separator_char: optional, indicates that the value can be separated into chunks by the given character.
        """
        self._specs = specs
        self._value = value
        self._separator_char = separator_char
        # indices where the separator occurs
        self._separator_indices = [i for i, n in enumerate(value) if n == separator_char]

    def _transform_left(self, i):
        """ Returns either the given index or the index of the character next to the i'th separator. """
        if self._separator_char:
            return self._separator_indices[i - 1] + 1 if i and i != 0 else i
        else:
            return i

    def _transform_right(self, i):
        """ Returns either the given index or the index of the i'th separator. """
        if self._separator_char:
            return self._separator_indices[i-1] if i and i != 0 else i
        else:
            return i

    @staticmethod
    def is_type(value) -> bool:
        """ Returns whether the value can be sliced by this slicer. """
        return True  # This method should be overwritten by the derived class.

    def slice(self) -> str:
        """ Returns the sliced value. """
        result = []
        # Splits the value into parts separated by the specified char. If no separator is given no splitting occurs.
        parts = self._value.split(self._separator_char) if self._separator_char else self._value
        for spec in self._specs:
            if isinstance(spec, List):
                # The left and right index e.g. [0:1] with l = 0 and r = 1
                l, r = spec
                # Do the slicing based on the provided indices. If necessary transform the indices.
                result.append((self._value[slice(self._transform_left(l), self._transform_right(r))]))
            else:
                # There was only one index provided, so we select the corresponding part directly.
                result.append(parts[spec])
        # Return the sliced value whereby joining the individual results again with the provided separator char.
        return self._separator_char.join(result)


class MacSlicer(BasicSlicer):
    """
    Slicer for a mac address.

    mac == 00:83:00:20:20:83
    mac[0] == 00
    mac[:2] == 00:83
    mac[1-2] == 00:83
    mac[1-2,1-2] == 00:83:00:83

    """

    def __init__(self, specs, value: Any):
        if ':' in value:
            # Mac address is separated by colons (:).
            super().__init__(specs, value, ':')
        elif '-' in value:
            # Mac address is separated by dashes (-).
            super().__init__(specs, value, '-')
        elif '.' in value:
            # Mac address is separated by dots (.).
            super().__init__(specs, value, '.')
        else:
            # The slicer-factory first calls the is_type method and only calls the __init__ method of the MacSlicer if
            # it returns True. As a result we expect that the mac-address is indeed valid and either separated by a
            # colon (:), a dash (-) or a dot (.). If not something clearly went wrong here.
            raise ProgrammingError('No valid separator found in "{}"!'.format(value))

    @staticmethod
    def is_type(value) -> bool:
        """ Checks whether the given value is a mac address. """
        try:
            pp.common.mac_address.parseString(value, parse_all=True)
            return True
        except:
            return False


class IPv4Slicer(BasicSlicer):
    """
    Slicer for IPv4 addresses.

    ipv4 == 127.0.0.1
    ipv4[0] == 127
    ipv4[0,1] == 127.0
    ipv4[:2] == 127.0
    ipv4[1-2] == 127.0
    ipv4[1-2,1-2] == 127.0.127.0

    """

    def __init__(self, specs, value):
        super().__init__(specs, ipaddress.IPv4Address(value).exploded, '.')

    @staticmethod
    def is_type(value) -> bool:
        """ Checks whether the given value is an ipv4 address. """
        try:
            pp.common.ipv4_address.parseString(value, parse_all=True)
            return True
        except:
            return False


class IPv6Slicer(BasicSlicer):
    """
    Slicer for IPv6 addresses.

    ipv6 == 2001:0db8:85a3:0000:0000:8a2e:0370:7334
    ipv6[0] == 2001
    ipv6[:2] == 2001:0db8
    ipv6[1-2] == 2001:0db8
    ipv6[1-2,1-2] == 2001:0db8:2001:0db8

    """

    def __init__(self, specs, value):
        super().__init__(specs, ipaddress.IPv6Address(value).exploded, ':')

    @staticmethod
    def is_type(value) -> bool:
        """ Checks whether the value is an ipv6 address. """
        try:
            pp.common.ipv6_address.parseString(value, parse_all=True)
            return True
        except:
            return False
