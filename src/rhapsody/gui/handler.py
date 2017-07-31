# Copyright (c) Peter Majko.

"""
Rhapsody's gui handlers, designed to work with tkinter.
"""
from rhapsody.core.multiprocessing import PipeHandler


class TkPipeHandle(PipeHandler):
    """
    Multiprocessing's Pipe handler. Designed to work with Tkinter library.
    Inherit's from PipeHandle.

    Overrides self.read_loop so it can loop inside Tk root. The loop frequency
    is based on self.refresh_rate - number of loops per second.

    Overrides self.on_recv to be able to handle received data from outside of the class
    via any function passed as on_recv_handling_func init argument. The self._on_handling_func
    pointer can be later redirected to any function passed as argument into
    self.change_on_recv_handling_func.
    """

    def __init__(self, master, refresh_rate=30, on_recv_handling_func=None):
        """

        :param master: rhapsody.gui.application.BasicPipedApplication or any class which inherit's from it
        :param refresh_rate: number of read loops per second
        :param on_recv_handling_func: function/method to handle received data
        """
        super().__init__(master.conn, refresh_rate)
        self.master = master
        self.master.after(self.master.initial_after_delay, self.read_loop)
        self._on_recv_handling_func = on_recv_handling_func

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

    def on_recv(self, data):
        """
        Overrides self.on_recv to be able to handle received data from outside of the class
        via any function passed as on_recv_handling_func init argument. The self._on_handling_func
        pointer can be later redirected to any function passed as argument into
        self.change_on_recv_handling_func.
        :param data: any object sent by the other side of the Pipe
        :return: -
        """
        if not self._on_recv_handling_func:
            pass
        else:
            self._on_recv_handling_func(data)

    def change_on_recv_handling_func(self, func):
        """
        Self explanatory - I hope :)
        :param func: Function/method which should handle the data sent by other side of Pipe
        :return: -
        """
        self._on_recv_handling_func = func
