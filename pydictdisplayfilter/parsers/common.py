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
import re
from collections import deque

import pyparsing as pp
import dacite
from ipranger.ipranger import IPAddresses, IPRangerFormatParser


def _quoted_string():
    return pp.QuotedString("'") | pp.QuotedString('"')


def _safe_word():
    return pp.Word(
        pp.printables
            .replace('(', '').replace(')', '')
            .replace('[', '').replace(']', '')
            .replace('{', '').replace('}', '')
    )


def _signed_float():
    return pp.Combine(pp.Optional('-') + pp.Word(pp.nums) + pp.Optional('.' + pp.Word(pp.nums))).setParseAction(
        lambda tokens: list(map(float, tokens.as_list()))
    )


def _number():
    return pp.common.integer


def _string_list():
    return pp.delimitedList(
        _quoted_string()
    ).addParseAction(lambda tokens: [tokens.asList()])


def _number_list():
    """ e.g. "1", "1,2,3", "1-3", "0..3" """
    signed_float = _signed_float()
    return pp.delimitedList(
        pp.Group(signed_float + pp.Literal('..') + signed_float) |
        pp.Group(signed_float + pp.Literal('-') + signed_float) |
        signed_float
    ).addParseAction(lambda tokens: [tokens.asList()])


def _ip_v4_list():
    """ e.g. '127.0.0.1', '192.168.0.1/24', '192.168.0.1-10', '192.168-169.1,2,3', ... """
    return IPRangerFormatParser.IP_ADDRESSES.setParseAction(
        lambda tokens: [[dacite.from_dict(IPAddresses, tokens.as_dict())]]
    )


def _slice():
    """ e.g. [0:1], [0,1,2], [:1], [1:], ... """

    def _parse(specs):  # -> List[List[int, str, int]]
        """ Parses a comma-separated list of slicing specifications. """
        result = []
        for spec in specs:
            l, r = get_spec_values(spec)
            if ':' in spec:
                # '0:1', ':1' --> [0, 1]
                # '1:' --> [1, None]
                result.append(list(map(lambda i: int(i) if i or i == 0 else None, [l, r])))
            elif '-' in spec:
                # 1-2 --> [0, 2]
                # -1-2 --> [-2, 2]
                # -1--2 --> [-2, -2]
                result.append([l - 1, r])
            else:
                # 1
                # -1
                result.append(spec[0])
        return result

    def get_spec_values(spec):
        """
        Gets the left and the right value.

        Examples:

            '1:2' -> 1, 2
            ':1'  -> None, 1
            '1:'  -> 1, None

        """
        spec = deque(spec)
        if isinstance(spec[0], int):
            # if the first element is an integer, pad with None values to the right
            spec.extend([None] * (3 - len(spec)))
        else:
            # Otherwise, pad with None values starting from the left
            spec.extendleft([None] * (3 - len(spec)))
        # Return the first and the third item. The second item (operator) is ignored.
        return spec[0], spec[2]

    number = pp.common.signed_integer
    return pp.Literal('[').suppress() + (
        (
            pp.delimitedList((
                    pp.Group(number + pp.Literal(':') + number) |
                    pp.Group(number + pp.Literal(':')) |
                    pp.Group(pp.Literal(':') + number) |
                    pp.Group(number + pp.Literal('-') + number) |
                    pp.Group(number)
            ), delim=',')
        ).setParseAction(lambda tokens: [_parse(tokens.as_list())])
    ) + pp.Literal(']').suppress()


white = pp.White(' ').suppress()
quotedString = _quoted_string()
safeWord = _safe_word()
signedFloat = _signed_float()
stringList = _string_list()
numberList = _number_list()
ipv4List = _ip_v4_list()
slice = _slice()
