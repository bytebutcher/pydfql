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
import unittest

import pexpect as pexpect

EXAMPLE_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples', 'csv_display_filter.py'))
EXAMPLE_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'csv_example.csv'))


class TestCSVDisplayFilter(unittest.TestCase):

    def test_fields(self):
        child = pexpect.spawn(f'python {EXAMPLE_SCRIPT} {EXAMPLE_DATA}', timeout=2)
        child.expect('> ')
        child.sendline('fields')
        child.expect('> ')
        expected_output = '\r\n'.join([
            'fields', 'name', 'actor', 'age', 'gender', 'killed'
        ]) + '\r\n'
        self.assertEqual(expected_output, child.before.decode())
        child.close()

    def test_filter(self):
        child = pexpect.spawn(f'python {EXAMPLE_SCRIPT} {EXAMPLE_DATA}', timeout=2)
        child.expect('> ')
        child.sendline('filter name == Neo')
        child.expect('> ')
        self.assertIn('1 row in set', child.before.decode())
        child.close()
