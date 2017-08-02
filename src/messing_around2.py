# Copyright (c) Peter Majko.


from rhapsody.gui.application import SimpleConsoleApplication, create_app_process, start_app
from multiprocessing import Process

if __name__ == '__main__':

    p, parent_conn_ = create_app_process(SimpleConsoleApplication,
                                         {'title': 'Simple Console 1', 'x_modifier': 0.33})
    p2 = Process(target=start_app, kwargs={'app': SimpleConsoleApplication, 'kwargs': {'pipe_conn': parent_conn_,
                                                                                       'title': 'C2',
                                                                                       'x_modifier': 1}})
    p3 = Process(target=start_app, kwargs={'app': SimpleConsoleApplication, 'kwargs': {'pipe_conn': parent_conn_,
                                                                                       'title': 'C3',
                                                                                       'x_modifier': 1.67}})
    p.start()
    p2.start()
    p3.start()
    p.join()
    p2.join()
    p3.join()
