# Copyright (c) Peter Majko.

"""
Rhapsody's networking handlers, designed to work with twisted.
"""
from rhapsody.core.multiprocess import AdvancedPipeHandler
from twisted.internet import task
import time

class TwistedPipeHandler(AdvancedPipeHandler):
    """
    Multiprocessing's Advanced Pipe Handler designed to work with Twisted library.

    Overrides self.read_loop so it can loop inside Twisted.
    """

    def __init__(self, pipe_conn, refresh_rate=30, on_recv_handle=None):
        """
        :param master: rhapsody.networking.PTCPServer or any class which inherit's from it
        """
        super().__init__(conn=pipe_conn, refresh_rate=refresh_rate, on_recv_handle=on_recv_handle)
        self.read_loop_task = task.LoopingCall(self.read_loop)
        self.read_loop_task.start(1.0/refresh_rate)

    def read_loop(self):
        """
        Overrides self.read_loop so it can loop inside Twisted. The loop frequency
        is based on self.refresh_rate - number of loops per second.
        :return: -
        """
        try:
            self.read_non_blocking()
        except BrokenPipeError:
            self.on_recv('ERR: BrokenPipeError')
