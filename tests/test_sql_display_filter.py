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
import sqlite3
import unittest
from typing import List, Dict, Tuple

from parameterized import parameterized

from pydictdisplayfilter.display_filters import SQLDisplayFilter


class TestSQLDisplayFilter(unittest.TestCase):
    # List of dictionaries representing the data to filter on taken from TestDictDisplayFilter.
    # Tests for nested and mixed data were removed since they are not supported by SQL.
    data = [
        {'name': 'Morpheus', 'age': 38, 'gender': 'male', 'killed': False, 'power': None},
        {'name': 'Neo', 'age': 35, 'gender': 'male', 'killed': False, 'power': 'flight'},
        {'name': 'Cipher', 'age': 48, 'gender': 'male', 'killed': True, 'power': None},
        {'name': 'Trinity', 'age': 32, 'gender': 'female', 'killed': False, 'power': None}
    ]
    net_data = [
        {'ipv4': '10.2.2.2', 'ipv6': '2001:db8:0:0:0:0:1428:57ab', 'mac': '00:83:00:20:20:83', 'ports': '22'},
        {'ipv4': '192.168.0.1', 'ipv6': '2001:0db8:0000:08d3:0000:8a2e:0070:7344', 'mac': '00:83:00:20:20:83', 'ports': None},
    ]
    date_data = [
        {'title': 'Matrix', 'published': '1999/06/17'},
        {'title': 'Matrix Revolutions', 'published': '2003/05/11'},
        {'title': 'Matrix Reloaded', 'published': '2003/05/22'},
        {'title': 'Matrix Resurrections', 'published': '2021/12/23'}
    ]

    @classmethod
    def setUpClass(cls):
        # Setup in memory sqlite database.
        cls._connection = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
        # Add adapter and converter for handling boolean values.
        sqlite3.register_adapter(bool, int)
        sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
        # Create tables.
        TestSQLDisplayFilter._create_table(cls._connection, 'data', [
            ('name', 'text'), ('age', 'integer'), ('gender', 'text'), ('killed', 'boolean'), ('power', 'text')
        ], cls.data)
        TestSQLDisplayFilter._create_table(cls._connection, 'net_data', [
            ('ipv4', 'text'), ('ipv6', 'text'), ('mac', 'text'), ('ports', 'text')
        ], cls.net_data)
        TestSQLDisplayFilter._create_table(cls._connection, 'date_data', [
            ('title', 'text'), ('published', 'text')
        ], cls.date_data)

    @staticmethod
    def _create_table(connection: sqlite3.Connection, table_name: str, table_format: List[Tuple], table_data: List[Dict]):
        def _build_create_table_command():
            table_columns = ['id integer PRIMARY KEY']
            for column_name, column_type in table_format:
                table_columns.append(f'{column_name} {column_type}')
            return f'CREATE TABLE {table_name} (' + f', '.join(table_columns) + ');'

        def _build_insert_table_data_command():
            column_names = ', '.join([column_name for column_name, column_value in table_data[0].items()])
            column_values = ', '.join(['?' for _ in table_data[0].items()])
            return f'INSERT INTO {table_name} ({column_names}) VALUES({column_values});'

        create_table_command = _build_create_table_command()
        print(create_table_command)
        connection.execute(create_table_command)
        insert_table_data_command = _build_insert_table_data_command()
        for table_data_row in table_data:
            data = tuple(table_data_row.values())
            connection.execute(insert_table_data_command, data)

    @parameterized.expand([
        # Field existence
        ['name', 4],
        ['power', 1],
        ['not power', 3],
        # Comparison operators
        ['name == Neo', 1],
        ['name == \x4e\x65\x6f', 1],
        ['killed == True', 1],
        ['gender == male', 3],
        ['age == 32', 1],
        ['age >= 32', 4],
        ['age > 32', 3],
        ['age <= 32', 1],
        ['age <= 040', 1],  # octal value
        ['age <= 0x20', 1],  # hexadecimal value
        ['age < 32', 0],
        ['age ~= 3', 3],  # contains operator
        ['age ~ 3', 3],  # matches operator
        ['age & 0x20', 4],  # bitwise and operator
        # In operator
        ['age in { 32, 35, 38 }', 3],
        ['age in { 30..40 }', 3],
        ['age in { 30-40 }', 3],
        ['age in { 30.0..40.0 }', 3],
        ['name in { "Neo", "Trinity" }', 2],
        # logical operators
        ['age >= 32 and gender == male', 3],
        ['name == Neo or name == Trinity', 2],
        ['gender == female xor power', 2],
        ['gender == male and (age > 30 and age < 40)', 2],
        ['gender == male and not (age > 35)', 1],
        ['gender == male and !(age > 35)', 1],
        # Functions
        ('len(name) == 3', 1),
        ('upper(name) == NEO', 1),
        ('lower(name) == neo', 1),
        # Slice Operator
        ('gender[0] == m', 3),
        ('gender[-1] == e', 4),
        ('gender[0:2] == ma', 3),
        ('gender[:2] == ma', 3),
        ('gender[2:] == le', 3),
        ('gender[1-2] == ma', 3),
        ('gender[0,1] == ma', 3),
        ('gender[:2,3-4] == male', 3)
    ])
    def test_dict_display_filter_returns_correct_number_of_items(self, display_filter, no_items):
        self.assertEqual(len(list(SQLDisplayFilter(self._connection, 'data').filter(display_filter))), no_items)

    @parameterized.expand([
        ('published > 2000', 3),
        ('published < 2000', 1),
        ('published <= 2003/05/11', 2),
        ('published <= 2003-05-11', 2),
    ])
    def test_dict_display_filter_date_returns_correct_number_of_items(self, display_filter, no_items):
        self.assertEqual(len(list(SQLDisplayFilter(self._connection, 'date_data').filter(display_filter))), no_items)

    @parameterized.expand([
        # Comparison operators
        ['ipv4 == 10.2.2.2', 1],
        # In operator
        ['ipv4 in { 10.2.2.2/24 }', 1],
        # MAC slicing
        ['mac[0] == 00', 2],
        ['mac[:2] == 00:83', 2],
        ['mac[1-2] == 00:83', 2],
        ['mac[1-2,1-2] == 00:83:00:83', 2],
        # IPv4 slicing
        ['ipv4[0] == 10', 1],
        ['ipv4[0:2] == 10.2', 1],
        ['ipv4[:2] == 10.2', 1],
        ['ipv4[1-2] == 10.2', 1],
        ['ipv4[0,1] == 10.2', 1],
        ['ipv4[1-2,1-2] == 10.2.10.2', 1],
        # IPv6 comparison - recognizes standard and compact ipv6 addresses
        ['ipv6 == 2001:0db8:0000:08d3:0000:8a2e:0070:7344 and ipv6 == 2001:db8:0:8d3:0:8a2e:70:7344', 1],
        ['ipv6 == 2001:db8:0:0:0:0:1428:57ab and ipv6 == 2001:db8::1428:57ab', 1],
        # IPv6 slicing
        ['ipv6[0] == 2001', 2],
        ['ipv6[:2] == 2001:0db8', 2],
        ['ipv6[1-2] == 2001:0db8', 2],
        ['ipv6[1-2,1-2] == 2001:0db8:2001:0db8', 2],
    ])
    def test_net_dict_display_filter_returns_correct_number_of_items(self, display_filter, no_items):
        self.assertEqual(len(list(SQLDisplayFilter(self._connection, 'net_data').filter(display_filter))), no_items)
