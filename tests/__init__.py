import unittest


class TestCase(unittest.TestCase):

    def assertRaisesException(self, handler, message, exception_type=Exception):
        result = False
        try:
            handler()
        except exception_type:
            result = True
        self.assertTrue(result, message)
