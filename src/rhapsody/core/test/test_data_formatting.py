# Copyright (c) Peter Majko.

"""
Unit tests for rhapsody.core.data_formatting
"""

import unittest
from rhapsody.core.data_formatting import pretty


class PrettyFormatterTest(unittest.TestCase):

    def test_heterogeneous(self):
        test_dict = {
            'a': 0,
            1: 'b',
            pretty: [2, 3, (self, )]
        }
        expected_output = "{{\n" \
                          "\t'a': 0,\n" \
                          "\t1: 'b',\n" \
                          "\t{0}: [\n" \
                          "\t\t2,\n" \
                          "\t\t3,\n" \
                          "\t\t(\n" \
                          "\t\t\t{1}\n" \
                          "\t\t)\n" \
                          "\t]\n" \
                          "}}".format(repr(pretty), repr(self))
        self.assertEqual(pretty(test_dict), expected_output)
