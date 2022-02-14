from parameterized import parameterized

from pydictdisplayfilter.factories import SlicerFactory
from tests import TestCase
import pydictdisplayfilter.parsers.common as pc


class TestSliceParser(TestCase):

    slice_parser = pc.slice

    def slice_value(self, value, slice_spec):
        spec = self.slice_parser.parseString(slice_spec, parse_all=True).pop()
        return SlicerFactory().create(spec, value).slice()

    @parameterized.expand([
        ["Neo", "[0]"],
        ["Neo", "[-1]"],
        ["Neo", "[0:2]"],
        ["Neo", "[0:]"],
        ["Neo", "[:2]"],
        ["Neo", "[2:0]"],
    ])
    def test_slice_operator_behaves_like_python_slice_operator(self, value, slice_spec):
        """ Tests whether the implementation of the slice operator behaves like the one of python. """
        expected_result = eval('value' + slice_spec)  # e.g. value[0]
        self.assertEqual(self.slice_value(value, slice_spec), expected_result)

    @parameterized.expand([
        # support string slicing
        ["Neo", "[0]", 'N'],
        ["Neo", "[0,1]", 'Ne'],
        ["Neo", "[1-2]", 'Ne'],
        ["Neo", "[0:2]", 'Ne'],
        ["Neo", "[1:]", 'eo'],
        ["Neo", "[:2]", 'Ne'],
        # support ipv4 slicing
        ["127.0.0.1", "[0]", "127"],
        ["127.0.0.1", "[0,1]", "127.0"],
        ["127.0.0.1", "[1-2]", "127.0"],
        ["127.0.0.1", "[0:2]", "127.0"],
        ["127.0.0.1", "[1:]", "0.0.1"],
        ["127.0.0.1", "[:2]", "127.0"],
        # support ipv6 slicing
        ["2001:0db8:85a3:0000:0000:8a2e:0370:7334", "[0]", "2001"],
        ["2001:0db8:85a3:0000:0000:8a2e:0370:7334", "[0,1]", "2001:0db8"],
        ["2001:0db8:85a3:0000:0000:8a2e:0370:7334", "[1-2]", "2001:0db8"],
        ["2001:0db8:85a3:0000:0000:8a2e:0370:7334", "[0:2]", "2001:0db8"],
        ["2001:0db8:85a3:0000:0000:8a2e:0370:7334", "[1:]", "0db8:85a3:0000:0000:8a2e:0370:7334"],
        ["2001:0db8:85a3:0000:0000:8a2e:0370:7334", "[:2]", "2001:0db8"],
        # support mac slicing (separated by colons ':)
        ["00:83:00:20:20:83", "[0]", "00"],
        ["00:83:00:20:20:83", "[0,1]", "00:83"],
        ["00:83:00:20:20:83", "[1-2]", "00:83"],
        ["00:83:00:20:20:83", "[0:2]", "00:83"],
        ["00:83:00:20:20:83", "[1:]", "83:00:20:20:83"],
        ["00:83:00:20:20:83", "[:2]", "00:83"],
        # support mac slicing (separated by dashes '-')
        ["00-83-00-20-20-83", "[0]", "00"],
        ["00-83-00-20-20-83", "[0,1]", "00-83"],
        ["00-83-00-20-20-83", "[1-2]", "00-83"],
        ["00-83-00-20-20-83", "[0:2]", "00-83"],
        ["00-83-00-20-20-83", "[1:]", "83-00-20-20-83"],
        ["00-83-00-20-20-83", "[:2]", "00-83"],
        # support mac slicing (separated by dashes '.')
        ["00.83.00.20.20.83", "[0]", "00"],
        ["00.83.00.20.20.83", "[0,1]", "00.83"],
        ["00.83.00.20.20.83", "[1-2]", "00.83"],
        ["00.83.00.20.20.83", "[0:2]", "00.83"],
        ["00.83.00.20.20.83", "[1:]", "83.00.20.20.83"],
        ["00.83.00.20.20.83", "[:2]", "00.83"],
    ])
    def test_slice_operator_extends_python_slice_operator(self, value, slice_spec, expected_result):
        """ Tests whether the additional slicers which are not directly supported by python work as expected. """
        self.assertEqual(self.slice_value(value, slice_spec), expected_result)
