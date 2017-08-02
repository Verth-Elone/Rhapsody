# Copyright (c) Peter Majko.

import logging


class Logger(logging.Logger):

    def __init__(self, name, level):
        super().__init__(name=name, level=level)
            self.name =name
