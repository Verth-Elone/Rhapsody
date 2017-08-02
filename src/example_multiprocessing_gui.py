# Copyright (c) Peter Majko.


from rhapsody.gui.application import SimpleConsoleApplication
from rhapsody.core.multiprocessing import create_piped_process


if __name__ == '__main__':
    """
        Just a simple test :) write something into one app's input field, hit enter and it
        should appear in the other's output field - and vice versa.
        """
    p, parent_conn_ = create_piped_process(class_=SimpleConsoleApplication,
                                           start_method_name='mainloop',
                                           kwargs={'title': 'Simple Console 1',
                                                   'x_modifier': 0.33})
    p2, parent2_conn_ = create_piped_process(class_=SimpleConsoleApplication,
                                             start_method_name='mainloop',
                                             kwargs={'title': 'Simple Console 2',
                                                     'x_modifier': 1.66})
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
