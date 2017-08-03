# Copyright (c) Peter Majko.

"""
Rhapsody's multiprocessing module.
"""
import time
from multiprocessing import Process, Pipe


def create_piped_process(class_, start_method_name, kwargs={}):
    """
    Creates the Pipe() with two connection points.
    Creates the class_ instance in the separate process and runs its' start_method_name
    method when process.start().
    :param class_: Any class which is designed for running in it's own process
    :param start_method_name: Method of the class_ which is run when process.start()
    :param kwargs: Dictionary of arguments for the init of class_
    :return: tuple of Process and Pipe's parent_conn
    """
    parent_conn, child_conn = Pipe()
    kwargs['pipe_conn'] = child_conn
    process = Process(target=build_and_start_inside_process,
                      kwargs={'class_': class_,
                              'start_method_name': start_method_name,
                              'kwargs': kwargs})
    return process, parent_conn


def build_and_start_inside_process(class_, start_method_name, kwargs={}):
    """
    This is needed in the case that the object created based on the class must be initialized
    in the separate process.
    :param class_: Class which is to be initialized in the separate process
    :param start_method_name: Method of the class_ which is run when process.start()
    :param kwargs: dictionary of arguments for the class_ instance initialization
    :return: -
    """
    instance = class_(**kwargs)
    eval('instance.{sm}()'.format(sm=start_method_name))


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


class AdvancedPipeHandler(PipeHandler):
    """
    Multiprocessing Pipe's handler. Inherit's from PipeHandle.

    Overrides self.on_recv to be able to handle received data from outside of the class
    via any function passed as on_recv_handle init argument. The self._on_handling_func
    pointer can be later redirected to any function passed as argument into
    self.change_on_recv_handle.
    """

    def __init__(self, conn, refresh_rate=60, on_recv_handle=None):
        """
        :param on_recv_handle: function/method to handle received data
        """
        super().__init__(conn=conn, refresh_rate=refresh_rate)
        self._on_recv_handle = on_recv_handle

    def on_recv(self, data):
        """
        Overrides self.on_recv to be able to handle received data from outside of the class
        via any function passed as on_recv_handle init argument. The self._on_handling_func
        pointer can be later redirected to any function passed as argument into
        self.change_on_recv_handle.
        :param data: any object sent by the other side of the Pipe
        :return: -
        """
        if not self._on_recv_handle:
            pass
        else:
            self._on_recv_handle(data)

    def change_on_recv_handle(self, handle):
        """
        Self explanatory - I hope :)
        :param handle: Function/method which should handle the data sent by other side of Pipe
        :return: -
        """
        # TODO - check if handle has at least one argument - for data
        self._on_recv_handle = handle
