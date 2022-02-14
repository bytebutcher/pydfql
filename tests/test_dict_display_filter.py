import unittest

from parameterized import parameterized

from pydictdisplayfilter.display_filters import DictDisplayFilter


class TestDictDisplayFilter(unittest.TestCase):
    # List of dictionaries representing the data to filter on.
    data = [
        {"name": "Morpheus", "age": 38, "gender": "male", "killed": False},
        {"name": "Neo", "age": 35, "gender": "male", "killed": False, "power": ["flight", "bullet-time"]},
        {"name": "Cipher", "age": 48, "gender": "male", "killed": True},
        {"name": "Trinity", "age": 32, "gender": "female", "killed": False}
    ]
    data_nested = [
        {"name": "Morpheus", "age": {"born": "1961"}, "gender": "male"},
        {"name": "Neo", "age": {"born": "1964"}, "gender": "male"},
        {"name": "Cipher", "age": {"born": "1951"}, "gender": "male"},
        {"name": "Trinity", "age": {"born": "1967"}, "gender": "female"}
    ]
    data_listed = [
        {"name": ["Laurence", "Fishburne"], "age": {"born": "1961"}, "gender": "male"},
        {"name": ["Keanu", "Reeves"], "age": {"born": "1964"}, "gender": "male"},
        {"name": ["Joe", "Pantoliano"], "age": {"born": "1951"}, "gender": "male"},
        {"name": ["Carrie-Anne", "Moss"], "age": {"born": "1967"}, "gender": "female"}
    ]
    net_data = [
        {"ipv4": "10.2.2.2", "ipv6": "2001:db8:0:0:0:0:1428:57ab", "mac": "00:83:00:20:20:83", "ports": [22]},
        {"ipv4": "192.168.0.1", "ipv6": "2001:0db8:0000:08d3:0000:8a2e:0070:7344", "mac": "00:83:00:20:20:83", "ports": []},
    ]
    date_data = [
        {"title": "Matrix", "published": '1999/06/17'},
        {"title": "Matrix Revolutions", "published": '2003/05/11'},
        {"title": "Matrix Reloaded", "published": '2003/05/22'},
        {"title": "Matrix Resurrections", "published": '2021/12/23'}
    ]
    mixed_data = [
        {"n/a": "n/a"},
        {"value": ""},
        {"value": "0"},
        {"value": 0},
        {"value": "0.0"},
        {"value": 0.0},
        {"value": "0j"},
        {"value": 0j},
        {"value": "-1"},
        {"value": -1},
        {"value": "-1.0"},
        {"value": -1.0},
        {"value": 1},
        {"value": "1"},
        {"value": 1.0},
        {"value": "1.0"},
        {"value": 1.5},
        {"value": "1.5"},
        {"value": 2.5},
        {"value": "2.5"},
        {"value": "abcd"},
        {"value": "1999/06/17"},
        {"value": "10.2.2.2"},
        {"value": "2001:db8:0:0:0:0:1428:57ab"},
        {"value": "00:83:00:20:20:83"},
        {"value": [-1, 1, "1.5", 2.5, "a"] },
        {"value": ["a", "b"]},
        {"value": []},
        {"value": {"x": "y"}},
        {"value": {}},
        {"value": True},
        {"value": "True"},
        {"value": False},
        {"value": "False"},
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
    def test_dict_display_filter_returns_correct_number_of_items(self, display_filter, no_items):
        self.assertEqual(len(list(DictDisplayFilter(self.data).filter(display_filter))), no_items)

    @parameterized.expand([
        ('published > 2000', 3),
        ('published < 2000', 1),
        ('published <= 2003/05/11', 2),
        ('published <= 2003-05-11', 2),
    ])
    def test_dict_display_filter_date_returns_correct_number_of_items(self, display_filter, no_items):
        self.assertEqual(len(list(DictDisplayFilter(self.date_data).filter(display_filter))), no_items)

    @parameterized.expand([
        ['age.born > 1960', 3],
        ['age.born > 1960 and age.born < 1970', 3],
    ])
    def test_nested_dict_display_filter_returns_correct_number_of_items(self, display_filter, no_items):
        self.assertEqual(len(list(DictDisplayFilter(self.data_nested).filter(display_filter))), no_items)

    @parameterized.expand([
        ['name == Keanu', 1],
        ['name ~= u', 2],
        ['name ~ .*e$', 3],
    ])
    def test_listed_dict_display_filter_returns_correct_number_of_items(self, display_filter, no_items):
        self.assertEqual(len(list(DictDisplayFilter(self.data_listed).filter(display_filter))), no_items)

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
        self.assertEqual(len(list(DictDisplayFilter(self.net_data).filter(display_filter))), no_items)

    @parameterized.expand([
        # Fields
        ["value", len(mixed_data) - 4],
        ["not value", 4],
        # Numbers
        ["value == 1", 5],
        ["value != 1", len(mixed_data) - 5],
        ["value == 1.0", 5],
        ["value != 1.0", len(mixed_data) - 5],
        ["value == 0", 4],
        ["value != 0", len(mixed_data) - 4],
        ["value == -1", 5],
        ["value != -1", len(mixed_data) - 5],
        ["value == 1.5", 3],
        ["value != 1.5", len(mixed_data) - 3],
        ["value == 2.5", 3],
        ["value != 2.5", len(mixed_data) - 3],
        # String
        ["value == ''", 1],
        ["value != ''", len(mixed_data) -1],
        ["value == abcd", 1],
        ["value != abcd", len(mixed_data) -1],
        # Illegal comparison operators for string.
        ["value >= abcd", 0],
        ["value <= abcd", 0],
        ["value > abcd", 0],
        ["value < abcd", 0],
        # Date
        ["value == 1999/06/17", 1],
        ["value != 1999/06/17", len(mixed_data) - 1],
        # Too many matching values for a sane test. Do not mix dates with other types.
        # ["value >= 1999/06/17", 1],
        # ["value <= 1999/06/17", 1],
        # ["value < 1999/06/17", 0],
        # ["value > 1999/06/17", 0],
        # IPv4
        ['value == 10.2.2.2', 1],
        ['value != 10.2.2.2', len(mixed_data) - 1],
        ['value >= 10.2.2.2', 1],
        ['value <= 10.2.2.2', 1],
        ['value > 10.2.2.2', 0],
        ['value < 10.2.2.2', 0],
        # IPv6
        ['value == 2001:db8:0:0:0:0:1428:57ab', 1],
        ['value != 2001:db8:0:0:0:0:1428:57ab', len(mixed_data) - 1],
        ['value >= 2001:db8:0:0:0:0:1428:57ab', 1],
        ['value <= 2001:db8:0:0:0:0:1428:57ab', 1],
        ['value > 2001:db8:0:0:0:0:1428:57ab', 0],
        ['value < 2001:db8:0:0:0:0:1428:57ab', 0],
        # Boolean
        ['value == True', 2],
        ['value != True', len(mixed_data) - 2],
        ['value == False', 2],
        ['value != False', len(mixed_data) - 2],
        # Illegal comparison operators for boolean.
        ['value > True', 0],
        ['value < True', 0],
        ['value <= True', 0],
        ['value >= True', 0],
        ['value > False', 0],
        ['value < False', 0],
        ['value <= False', 0],
        ['value >= False', 0],
        # MAC
        ['value == 00:83:00:20:20:83', 1],
        ['value != 00:83:00:20:20:83', len(mixed_data) - 1],
        # Illegal comparison operators for MAC.
        ['value <= 00:83:00:20:20:83', 0],
        ['value >= 00:83:00:20:20:83', 0],
        ['value < 00:83:00:20:20:83', 0],
        ['value > 00:83:00:20:20:83', 0],
    ])
    def test_mixed_data_display_filter_returns_correct_number_of_items(self, display_filter, no_items):
        items = list(DictDisplayFilter(self.mixed_data).filter(display_filter))
        if len(items) != no_items:
            list_difference = [item for item in self.mixed_data if item not in items]
            print(list_difference)
        self.assertEqual(len(items), no_items)
