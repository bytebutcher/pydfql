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
import pyparsing as pp
from typing import List, Union, Optional, Callable, Dict
from pydictdisplayfilter.exceptions import ParserError
from pydictdisplayfilter.models import Expression

import pydictdisplayfilter.parsers.common as pc


class DisplayFilterParser:
    """ A parser for a display filter. """

    def __init__(self, field_names: Optional[List[str]] = None, functions: Optional[Dict[str, Callable]] = None):
        """
        Initializes the DisplayFilterParser with a list of valid field names and possible functions.
        field_names: optional list of field names ought to be valid (e.g. 'column', 'table.column', ...).
                     if none is given, everything is possible.
        functions: optional list of functions for transforming values (e.g. 'len(column)', 'upper(column)', ...)
        """

        # Function
        # --------
        # Function name and field name enclosed in brackets
        function = lambda arguments: (
                pp.oneOf(functions.keys()) + pp.Literal('(').suppress() + arguments + pp.Literal(')').suppress()
        )

        # Field Name
        # ----------
        # Field names as specified - or alphanumeric string including '_', '-' and '.'
        field_name = pp.oneOf(field_names) if field_names else pp.Word(pp.alphanums + '_-.')

        # Slice
        # -----
        # A slice spec surrounded by square brackets (e.g. [:1,1:2,1-2,2])
        slice = pc.slice

        # Value
        # -----
        # Either single-quoted, double-quoted, unquoted value or a list of ip addresses, strings, or numbers enclosed
        # by curly braces.
        value = (
                pc.quotedString |
                pc.safeWord |
                pp.Literal('{').suppress() + (pc.ipv4List | pc.stringList | pc.numberList) + pp.Literal('}').suppress()
        )

        # Comparison Operators
        # --------------------
        # Comparison operators are transformed to the python representation.
        equal_operator = pp.oneOf(['==', 'eq'], caseless=True).setParseAction(lambda token: '==')
        not_equal_operator = pp.oneOf(['!=', 'neq'], caseless=True).setParseAction(lambda token: '!=')
        greater_than_or_equal_operator = pp.oneOf(['>=', 'ge'], caseless=True).setParseAction(lambda token: '>=')
        greater_than_operator = pp.oneOf(['>', 'gt'], caseless=True).setParseAction(lambda token: '>')
        less_than_or_equal_operator = pp.oneOf(['<=', 'le'], caseless=True).setParseAction(lambda token: '<=')
        less_than_operator = pp.oneOf(['<', 'lt'], caseless=True).setParseAction(lambda token: '<')
        contains_operator = pp.oneOf(['~=', 'contains'], caseless=True).setParseAction(lambda token: '~=')
        matches_operator = pp.oneOf(['~', 'matches'], caseless=True).setParseAction(lambda token: '~')
        in_operator = pp.CaselessLiteral('in').setParseAction(lambda token: 'in')
        bitwise_and_operator = pp.Literal('&')
        comparison_operator = (
                equal_operator | not_equal_operator |
                greater_than_or_equal_operator | greater_than_operator |
                less_than_or_equal_operator | less_than_operator |
                contains_operator | matches_operator | in_operator |
                bitwise_and_operator
        )

        # Logical Operators
        # -----------------
        # Logical Operators are transformed to the python representation (e.g. not, and, or, ^).
        not_operator = pp.CaselessLiteral('not') + pc.white | pp.CaselessLiteral('!').setParseAction(lambda token: 'not')
        and_operator = pp.oneOf(['&&', 'and'], caseless=True).setParseAction(lambda token: 'and')
        or_operator = pp.oneOf(['||', 'or'], caseless=True).setParseAction(lambda token: 'or')
        xor_operator = pp.oneOf(['^^', 'xor'], caseless=True).setParseAction(lambda token: '^')
        logical_operator = pc.white + (and_operator | or_operator | xor_operator) + pc.white

        # Expression
        # ----------
        expression = pp.Forward()

        # Function including field name, comparison operator and value - if function is specified
        expression |= (function(field_name) + pc.white + comparison_operator + pc.white + value).setParseAction(
            # field name, comparison operator, value, function
            lambda tokens: [tokens[1], tokens[2], tokens[3], functions.get(tokens[0])]
        ) if functions else pp.Forward()

        # Function including field name with slice, comparison operator and value - if function is specified
        expression |= (
                function(field_name + slice) + pc.white() + comparison_operator + pc.white + value).setParseAction(
            # field name, comparison operator, value, function, slice
            lambda tokens: [tokens[1], tokens[3], tokens[4], functions.get(tokens[0]), tokens[2]]
        ) if functions else pp.Forward()

        # Field name, comparison operator and value
        expression |= (field_name + slice + pc.white + comparison_operator + pc.white + value).setParseAction(
            # field_name, comparison operator, value, function, slice
            lambda tokens: [tokens[0], tokens[2], tokens[3], None, tokens[1]]
        )

        # Field name, comparison operator and value
        expression |= (field_name + pc.white + comparison_operator + pc.white + value)

        # Field name
        expression |= field_name

        # Display Filter
        # --------------
        # Expressions connected with logical operators, optionally enclosed in parentheses.
        self._display_filter_format = pp.infixNotation(
            expression.addParseAction(lambda tokens: Expression(*tokens.asList())),
            [
                (not_operator, 1, pp.opAssoc.RIGHT),
                (logical_operator, 2, pp.opAssoc.LEFT),
            ]
        )

    def parse(self, format: str) -> List[Union[Expression, str]]:
        """
        Parses a display filter string.
        :param format: a display filter string. See class documentation for examples.
        :return a list of expressions and logical operators as string.
        :raises ParserError, when the given display filter could not be parsed correctly.
        """
        try:
            return self._display_filter_format.parseString(format, parseAll=True).asList()
        except Exception:
            # This error indicates that there is something wrong with the given display filter.
            # Especially if the given display filter is some kind of user input this error needs to be handled
            # accordingly.
            raise ParserError('Error parsing display filter!')
