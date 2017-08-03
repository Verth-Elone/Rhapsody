# Copyright (c) Peter Majko.

"""
Unit tests for rhapsody.core.data_formatting
"""

import unittest
from rhapsody.core.command import CommandProcessor
import json


def t_func(x, y, z=1):
    return x*y*z


class CommandProcessorTest(unittest.TestCase):
    def test_json(self):
        cmds = {
            't': t_func
        }
        cp = CommandProcessor(cmds)
        cp.log.setLevel(0)

        command_request_object = ['t', [2], {'y': 3, 'z': 4}]
        json_command_request_object = json.dumps(command_request_object)
        self.assertEqual(cp.process(json_command_request_object),
                         t_func(2, 3, 4))

    def test_args_kwargs(self):
        cmds = {
            't': t_func
        }
        cp = CommandProcessor(cmds)
        cp.log.setLevel(0)
        cl = [
            ['t', [2, 3, 4]],
            ['t', [2, 3], {'z': 4}],
            ['t', [], {'x': 2, 'y': 3, 'z': 4}]
        ]
        self.assertEqual(cp.process(cl[0]), cp.process(cl[1]))
        self.assertEqual(cp.process(cl[1]), cp.process(cl[2]))
