# Copyright (c) Peter Majko.

"""
Just a simple test :) write something into one app's input field, hit enter and it
should appear in the other's output field - and vice versa.
"""

from rhapsody.gui.application import SimpleConsoleApplication, create_app_process


if __name__ == '__main__':
    p, parent_conn_ = create_app_process(SimpleConsoleApplication,
                                         {'title': 'Simple Console 1', 'x_modifier': 0.5})
    p2, parent2_conn_ = create_app_process(SimpleConsoleApplication,
                                           {'title': 'Simple Console 2', 'x_modifier': 1.5})
    p.start()
    p2.start()

    import time
    time.sleep(0.1)

    while p.is_alive() and p2.is_alive():
        if parent_conn_.poll():
            parent2_conn_.send(parent_conn_.recv())
        if parent2_conn_.poll():
            parent_conn_.send(parent2_conn_.recv())
        time.sleep(0.01)
