# Copyright (c) Peter Majko.


from rhapsody.gui.application import SimpleConsoleApplication
from rhapsody.core.multiprocess import PipeHandler, create_piped_process
import logging


class LoggingPipeHandler(logging.Handler):
    def __init__(self, level, pipe_handler: PipeHandler):
        super().__init__(level)
        self.pipe_handler = pipe_handler

    def emit(self, record):
        log_entry = self.format(record)
        self.pipe_handler.send(log_entry)
        return True


class PipeStream:

    def __init__(self, pipe_handler: PipeHandler):
        self.pipe_handler = pipe_handler

    def write(self, msg):
        self.pipe_handler.send(msg)

    def flush(self):
        pass


if __name__ == '__main__':
    l = logging.getLogger()
    f = logging.Formatter('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s: %(message)s')
    h = logging.StreamHandler()
    h.setFormatter(f)
    h.setLevel(logging.DEBUG)
    l.addHandler(h)
    l.setLevel(logging.DEBUG)

    l.debug('test')

    p, parent_conn_ = create_app_process(SimpleConsoleApplication,
                                         {'title': 'Simple Console 1', 'x_modifier': 0.5})
    p.start()

    ph = PipeHandler(parent_conn_)
    h2 = LoggingPipeHandler(logging.DEBUG, ph)
    # h2 = logging.StreamHandler(PipeStream(ph))
    h2.setFormatter(logging.Formatter('%(name)s - %(levelname)s: %(message)s'))
    l.addHandler(h2)

    import time
    time.sleep(0.1)

    while p.is_alive():
        if parent_conn_.poll():
            d = parent_conn_.recv()
            l.info(d)
        time.sleep(0.1)
