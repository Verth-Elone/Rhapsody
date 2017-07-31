# Copyright (c) Peter Majko.

"""
Rhapsody's multiprocessing module.
"""
import time


class PipeHandler:
    """
    Handles python's standard multiprocessing library's Connection object created by Pipe.
    It is using time.sleep for self.read_loop().

    Override of self.read_loop and self.on_recv
    """

    def __init__(self, conn, refresh_rate=60):
        """
        :param conn: Python's standard multiprocessing.Connection
        :param refresh_rate: numeric, how many times per minute should read_loop run
        """
        self.conn = conn
        self.refresh_rate = refresh_rate
        self.reading = False

    def read_loop(self):
        """
        Can be overridden, as for example in rhapsody.gui.application.TkPipeHandler
        :return: -
        """
        self.reading = True
        while self.reading:  # should be more like 'while running:' or similar
            try:
                self.read_non_blocking()
            except BrokenPipeError:
                self.reading = False
            else:
                time.sleep(1/self.refresh_rate)

    def read_non_blocking(self):
        if self.conn.poll():
            self.on_recv(self.conn.recv())

    def on_recv(self, data):
        """
        Override
        :param data: object received by python's standard multiprocessing.Connection.recv()
        :return: -
        """
        pass

    def send(self, data):
        """
        Just moving send from connection to handler itself
        :param data: any object, see python's standard multiprocessing.Connection.send()
        :return:
        """
        self.conn.send(data)
