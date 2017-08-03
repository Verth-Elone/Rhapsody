# Copyright (c) Peter Majko.

"""
Rhapsody's gui handlers, designed to work with tkinter.
"""
from rhapsody.core.multiprocess import AdvancedPipeHandler


class TkPipeHandler(AdvancedPipeHandler):
    """
    Multiprocessing's Advanced Pipe Handler designed to work with Tkinter library.

    Overrides self.read_loop so it can loop inside Tk root.
    """

    def __init__(self, master, refresh_rate=30, on_recv_handle=None):
        """
        :param master: rhapsody.gui.application.BasicPipedApplication or any class which inherit's from it
        """
        super().__init__(conn=master.conn, refresh_rate=refresh_rate, on_recv_handle=on_recv_handle)
        self.master = master
        # start the read loop in init already - with delay
        self.master.after(self.master.initial_after_delay, self.read_loop)

    def read_loop(self):
        """
        Overrides self.read_loop so it can loop inside Tk root. The loop frequency
        is based on self.refresh_rate - number of loops per second.
        :return: -
        """
        try:
            self.read_non_blocking()
        except BrokenPipeError:
            self.on_recv('ERR: BrokenPipeError')
        else:
            self.master.after(round((1/self.refresh_rate)*1000), self.read_loop)
