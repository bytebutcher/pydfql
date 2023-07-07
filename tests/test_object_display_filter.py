# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of pydfql.
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
import dataclasses
import unittest
from typing import List

from parameterized import parameterized

from pydfql.display_filters import ObjectDisplayFilter


class Person:

    def __init__(self, name: str = '', age: int = 0, gender: str = '', killed: bool = False, power: List = None):
        self.name = name
        self.age = age
        self.gender = gender
        self.killed = killed
        self.power = power


class TestObjectDisplayFilter(unittest.TestCase):
    # List of objects representing the data to filter on.
    data = [
        Person(name="Morpheus", age=38, gender="male", killed=False),
        Person(name="Neo", age=35, gender="male", killed=False, power=["flight", "bullet-time"]),
        Person(name="Cipher", age=48, gender="male", killed=True),
        Person(name="Trinity", age=32, gender="female", killed=False),
    ]

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
    def test_object_display_filter_returns_correct_number_of_items(self, display_filter, no_items):
        self.assertEqual(len(list(ObjectDisplayFilter(self.data).filter(display_filter))), no_items)
