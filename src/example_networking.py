# Copyright (c) Peter Majko.

"""

"""
from rhapsody.networking.tcp_server import PTCPServer
from rhapsody.core.multiprocess import create_piped_process
from rhapsody.gui.application import SimpleConsoleApplication

if __name__ == '__main__':
    p, pc = create_piped_process(PTCPServer, 'start')
    p2, pc2 = create_piped_process(class_=SimpleConsoleApplication,
                                   start_method_name='mainloop',
                                   kwargs={'title': 'Simple Console 1', 'x_modifier': 3,
                                           'minsize': (1400, 800), 'maxsize': (1920, 1080)})
    p.start()
    p2.start()

    import time

    time.sleep(0.1)

    while p.is_alive() and p2.is_alive():
        if pc.poll():
            pc2.send(pc.recv())
        if pc2.poll():
            pc.send(pc2.recv())
        time.sleep(0.01)
