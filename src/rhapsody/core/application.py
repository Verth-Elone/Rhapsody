# Copyright (c) Peter Majko.

"""

"""
from rhapsody.core.command import CommandProcessor
from rhapsody.io.log import get_child_logger, get_default_logger


class AppBase:

    def __init__(self, logger=None):
        if not logger:
            logger = get_default_logger(self.__class__.__name__)
        self.log = logger
        self.commands = {}
        self.command_processor = CommandProcessor(self.commands, get_child_logger(self.log, 'CommandProcessor'))

    def get_unit(self):