# Copyright (c) Peter Majko.

"""
Rhapsody's logger module
"""

from rhapsody.core.multiprocess import PipeHandler
import logging


def get_default_logger(name=None):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        formatter = logging.Formatter(fmt='%(process)d|%(processName)s|%(thread)d|%(threadName)s|'
                                          '%(asctime)s|%(levelname)s|%(filename)s|%(name)s.%(funcName)s: %(message)s',
                                      datefmt='%d.%m.%Y %T')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger


def get_child_logger(parent_logger: logging.Logger, child_logger_name: str):
    logger = logging.getLogger('{pln}.{cln}'.format(pln=parent_logger.name, cln=child_logger_name))
    return logger


class LoggingPipeHandler(logging.Handler):
    """

    """
    def __init__(self, pipe_handler: PipeHandler, level=logging.NOTSET):
        super().__init__(level)
        self.pipe_handler = pipe_handler

    def emit(self, record):
        log_entry = self.format(record)
        self.pipe_handler.send(log_entry + '\n')


class PipeStream:
    """
    Simple stream which streams to the pipe connection
    """
    def __init__(self, pipe_handler: PipeHandler):
        self.pipe_handler = pipe_handler

    def write(self, msg):
        self.pipe_handler.send(msg)

    def flush(self):
        pass
