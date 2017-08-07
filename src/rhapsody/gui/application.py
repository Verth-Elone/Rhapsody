# Copyright (c) Peter Majko.

"""
Rhapsody's GUI application library
"""
import tkinter as tk
from rhapsody.gui.handler import TkPipeHandler
from rhapsody.gui.console import ConsoleFrame


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
        self.initial_after_delay = 1  # how long should all initial after functions wait
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
        self.conn_handler = TkPipeHandler(self, 60)


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
        self.conn_handler.change_on_recv_handle(self.console.write)
        # register handle's send method with the console's on input 'event'
        self.console.change_on_input_handle(self.conn_handler.send)
        # self.attributes('-fullscreen', True)  # full-screen
        self.wm_state('zoomed')  # maximize window
