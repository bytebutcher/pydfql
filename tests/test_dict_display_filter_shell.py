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
import io
import logging
import os
import unittest
from unittest import mock


from pydictdisplayfilter.helpers import DictDisplayFilterShell


class TestDictDisplayFilterShell(unittest.TestCase):

    data = [
        {"name": "Morpheus", "age": 38, "gender": "male", "killed": False},
        {"name": "Neo", "age": 35, "gender": "male", "killed": False, "power": ["flight", "bullet-time"]},
        {"name": "Cipher", "age": 48, "gender": "male", "killed": True},
        {"name": "Trinity", "age": 32, "gender": "female", "killed": False}
    ]

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_fields(self, mock_stdout):
        ddfs = DictDisplayFilterShell(self.data)
        expected_output = os.linesep.join([
            'age', 'gender', 'killed', 'name', 'power'
        ]) + os.linesep
        ddfs.do_fields()
        self.assertEqual(expected_output, mock_stdout.getvalue())

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_fields_fixed(self, mock_stdout):
        ddfs = DictDisplayFilterShell(self.data, field_names=[
            'age', 'gender', 'killed', 'name'
        ])
        expected_output = os.linesep.join([
            'age', 'gender', 'killed', 'name'
        ]) + os.linesep
        ddfs.do_fields()
        self.assertEqual(expected_output, mock_stdout.getvalue())


    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_filter(self, mock_stdout):
        ddfs = DictDisplayFilterShell(self.data)
        ddfs.do_filter('name == Neo')
        expected_output = '1 row in set'
        self.assertIn(expected_output, mock_stdout.getvalue())

    def test_filter_empty(self):
        ddfs = DictDisplayFilterShell(self.data)
        with self.assertLogs() as captured:
            ddfs.do_filter('')
        self.assertEqual(captured.records[0].levelno, logging.ERROR)
        self.assertEqual(captured.records[0].getMessage(), 'No arguments supplied to filter function.')

    def test_debug_mode(self):
        ddfs = DictDisplayFilterShell(self.data)
        with self.assertLogs() as captured:
            ddfs.do_debug()
        self.assertEqual(captured.records[0].levelno, logging.WARNING)
        self.assertEqual(captured.records[0].getMessage(), 'Debug mode enabled')
        with self.assertLogs() as captured:
            ddfs.do_debug()
        self.assertEqual(captured.records[0].levelno, logging.WARNING)
        self.assertEqual(captured.records[0].getMessage(), 'Debug mode disabled')
