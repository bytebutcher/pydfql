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
import os
from unittest import TestCase, mock
from unittest.mock import Mock, patch

from pydictdisplayfilter.helpers import TableColumnSizeCalculator, Table, DictTable


class TestTable(TestCase):

    def test_table_column_size_calculator(self):
        data = [{'a': '1234', 'aa': '2', 'aaa': '3'}]
        actual_result = TableColumnSizeCalculator.calculate(data, ['a', 'aa', 'aaa'])
        self.assertEqual([4, 2, 3], actual_result)

    @patch('time.time', mock.MagicMock(side_effect=[1,2]))
    def test_table_display_column_sizes(self):
        # time.time is mocked in order to get a deterministic query time result.
        query_time_result = '1.00 secs'
        # display_filter is mocked since it is not subject to the test.
        display_filter = Mock()
        display_filter.field_names = ['a', 'aa', 'aaa']
        display_filter.filter.return_value = [{'a': '1234', 'aa': '2', 'aaa': '3'}]
        # the mocked display filter returns the same result regardless of the filter term.
        expected_result = os.linesep.join([
            '',
            'a    | aa | aaa',
            '---- | -- | ---',
            '1234 | 2  | 3  ',
            '',
            f'1 row in set ({query_time_result})\n',
        ])
        self.assertEqual(expected_result, Table(display_filter).filter(''))

    @patch('time.time', mock.MagicMock(side_effect=[1,2]))
    def test_table_empty(self):
        # time.time is mocked in order to get a deterministic query time result.
        query_time_result = '1.00 secs'
        # display_filter is mocked since it is not subject to the test.
        display_filter = Mock()
        display_filter.field_names = []
        display_filter.filter.return_value = []
        # the mocked display filter returns the same result regardless of the filter term.
        expected_result = os.linesep.join([
            '',
            f'Empty set ({query_time_result})\n',
        ])
        self.assertEqual(expected_result, Table(display_filter).filter(''))

    def test_dict_table_fields(self):
        data_store = [
            {'a': '1234', 'aa': '2', 'aaa': '3'},
            {'b': '1234'},
            {'c': ['1', '2']},
            {'d': {'da': '4'}}
        ]
        expected_result = ['a', 'aa', 'aaa', 'b', 'c', 'd']
        self.assertEqual(expected_result, DictTable(data_store).fields())
