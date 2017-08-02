# Copyright (c) Peter Majko.

"""
Rhapsody's GUI application library
"""
import tkinter as tk
from multiprocessing import Process, Pipe
from rhapsody.gui.handler import TkPipeHandle
from rhapsody.gui.console import ConsoleFrame


def create_app_process(app, kwargs={}):
    """

    :param app: Some application class from this module
    :param kwargs: Dictionary of arguments for the init of app
    :return: tuple of Process and Pipe's parent_conn
    """
    parent_conn, child_conn = Pipe()
    kwargs['pipe_conn'] = child_conn
    process = Process(target=start_app, kwargs={'app': app, 'kwargs': kwargs})
    return process, parent_conn


def start_app(app, kwargs={}):
    """
    This is a MUST to initialize tkinter.Tk object in new process and not before!
    If tkinter.Tk is initialized in the parent Process and mainloop is passed as
    target of new child Process, Tcl dislikes that!
    :param app: tkinter.Tk or any class inheriting from it
    :param kwargs: see the app's __init__ for supported arguments
    :return: -
    """
    app = app(**kwargs)
    app.mainloop()


class BasicApplication(tk.Tk):
    """
    Just some basic tkinter structure, used for inheriting by more advanced structures mostly.
    I am not going into the detail of it's __init__ function. Wanna know more? Study tkinter.

    x_modifier - modifies window's spawn location on x axis.
        In the case of 3 monitors: -1 left monitor, +1 center monitor, +2 right monitor
        Use of float is possible.
    """

    def __init__(self,
                 title='app',
                 minsize=(640, 480),
                 maxsize=(640, 480),
                 x_modifier=1,
                 bg_color='white'):
        super().__init__()
        self.initial_after_delay = 500  # how long should all initial after functions wait
        self.title(title)
        self.minsize(*minsize)
        self.maxsize(*maxsize)
        self.configure(background=bg_color)
        width, height = minsize
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = x_modifier * (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.geometry('{w}x{h}+{x}+{y}'.format(
            w=width,
            h=height,
            x=int(x),
            y=int(y)
        ))


class BasicPipedApplication(BasicApplication):
    """
    By adding pipe connection and handler it is now possible for "app" to communicate
    when initialized in different process.
    """
    def __init__(self, pipe_conn, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = pipe_conn
        self.conn_handler = TkPipeHandle(self, 30)


class SimpleConsoleApplication(BasicPipedApplication):
    """
    Simple console application. Refer to BasicPipedApplication and ConsoleFrame
    for more information.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = ConsoleFrame(self)
        self.console.pack(fill='both', side='bottom', expand='True')
        # register ConsoleFrame's write method with handle's on receive 'event'
        self.conn_handler.change_on_recv_handling_func(self.console.write)
        # register handle's send method with the console's on input 'event'
        self.console.change_on_input_handling_func(self.conn_handler.send)


if __name__ == '__main__':
    """
    Just a simple test :) write something into one app's input field, hit enter and it
    should appear in the other's output field - and vice versa.
    """
    p, parent_conn_ = create_app_process(SimpleConsoleApplication,
                                         {'title': 'Simple Console 1'})
    p2, parent2_conn_ = create_app_process(SimpleConsoleApplication,
                                           {'title': 'Simple Console 2'})
    p.start()
    p2.start()

    import time

    time.sleep(0.1)

    while p.is_alive() and p2.is_alive():
        if parent_conn_.poll():
            parent2_conn_.send(parent_conn_.recv())
        if parent2_conn_.poll():
            parent_conn_.send(parent2_conn_.recv())
        time.sleep(1)
