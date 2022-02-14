# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of python-dict-display-filter.
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
from parameterized import parameterized

from pydictdisplayfilter.exceptions import ParserError
from pydictdisplayfilter.models import Expression
from pydictdisplayfilter.parsers import DisplayFilterParser
from tests import TestCase


class TestFilterStringParser(TestCase):
    display_filter_parser = DisplayFilterParser(['address', 'port', 'protocol', 'banner'])
    generic_display_filter_parser = DisplayFilterParser()

    @parameterized.expand([
        ['127.0.0.1'],
        ['127.0.0.1/24'],
        ['127.0.0.?'],
        ['127.*'],
        ['^asd$'],
        ['*asd*'],
        ['.asd.'],
    ])
    def test_value(self, value):
        self.display_filter_parser.parse("address == " + value)

    @parameterized.expand([
        ['127.0.0.1'],
        ['127.0.0.1/24'],
        ['127.0.0.?'],
        ['127.*'],
        ['^asd$'],
        ['*asd*'],
        ['.asd.'],
    ])
    def test_single_quoted_value(self, value):
        self.display_filter_parser.parse("address == '" + value + "'")

    @parameterized.expand([
        ['127.0.0.1'],
        ['127.0.0.1/24'],
        ['127.0.0.?'],
        ['127.*'],
        ['^asd$'],
        ['*asd*'],
        ['.asd.'],
    ])
    def test_invalid_mixed_quoted_value(self, value):
        self.assertRaisesException(
            lambda value: self.display_filter_parser.parse("address == \"" + value + "'"),
            value)

    @parameterized.expand([
        ['address'],
        ['port'],
        ['protocol'],
        ['banner'],
    ])
    def test_field_name(self, db_keyword):
        self.assertEqual(self.display_filter_parser.parse(db_keyword + " == 1"), [
            Expression(db_keyword, '==', '1')
        ])

    @parameterized.expand([
        ['address'],
        ['user.password'],
        ['user.user_name'],
        ['host-id'],
        ['host1'],
    ])
    def test_generic_field_name(self, db_keyword):
        self.assertEqual(self.generic_display_filter_parser.parse(db_keyword + ' == 1'), [
            Expression(db_keyword, '==', '1')
        ])

    @parameterized.expand([
        ['==', '=='], ['eq', '=='],
        ['!=', '!='], ['neq', '!='],
        ['>=', '>='], ['ge', '>='],
        ['<=', '<='], ['le', '<='],
        ['>', '>'], ['gt', '>'],
        ['<', '<'], ['lt', '<'],
    ])
    def test_comparison_operator(self, operator, key):
        self.assertEqual(self.display_filter_parser.parse('address ' + operator + ' 1'), [
            Expression('address', key, '1')
        ])

    @parameterized.expand([
        ['and'],
        ['or']
    ])
    def test_logical_operator(self, operator):
        self.assertEqual(self.display_filter_parser.parse('address == 1 ' + operator + ' address == 2'), [[
            Expression('address', "==", '1'),
            operator,
            Expression('address', '==', '2'),
        ]])

    @parameterized.expand([
        ['and'],
        ['or'],
    ])
    def test_logical_operators_name(self, operator):
        self.display_filter_parser.parse("address == 1 " + operator + " address == 2")

    def test_parentheses(self):
        self.assertEqual(self.display_filter_parser.parse("(address == 1)"), [
            Expression('address', '==', '1')
        ])

    @parameterized.expand([
        ["')'", ')'],
        ['")"', ')'],
    ])
    def test_quoted_value(self, quoted_value, unquoted_value):
        self.assertEqual(self.display_filter_parser.parse('(address == ' + quoted_value + ')'), [
            Expression('address', '==', unquoted_value)
        ])

    def test_complex_query(self):
        self.assertEqual(self.display_filter_parser.parse("address == 1 and (port == 1 or port == 2)"), [[
            Expression('address', "==", "1"),
            "and",
            [
                Expression('port', "==", "1"),
                "or",
                Expression('port', "==", "2")
            ]
        ]])

    @parameterized.expand([
        ['test'],  # invalid expression
        ['addresseqb'],  # should not be evaluated as address == b
        ['addresseqbandporteqc'],  # should not be evaluated as address == b and port == c
        ['address=='],  # missing value
        ['==address'],  # missing db_keyword
        ['address=test'],  # invalid operator
        ['test==test'],  # invalid db_keyword
        ['address==1 & address=1'],  # invalid logical operator
        ['()'],  # empty parentheses
        ['address==)'],  # parentheses needs to be in quotes
        ['address=="value\''],  # mixed quotes
        ['address==\'value"']  # mixed quotes
    ])
    def test_invalid_query(self, filter_string):
        self.assertRaisesException(lambda: self.display_filter_parser.parse(filter_string), filter_string)

    @parameterized.expand([
        ['address=='],  # missing value
        ['address=test'],  # invalid operator
        ['==test'],  # missing db_keyword
        ['test/3==test'],  # invalid db_keyword
        ['address==1 & address=1'],  # invalid logical operator
        ['()'],  # empty parentheses
        ['address==)'],  # parentheses needs to be in quotes
        ['address=="value\''],  # mixed quotes
        ['address==\'value"']  # mixed quotes
    ])
    def test_invalid_generic_query(self, filter_string):
        self.assertRaisesException(
            lambda: self.generic_display_filter_parser.parse(filter_string), filter_string, ParserError
        )
