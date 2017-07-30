# Copyright (c) Peter Majko.

import logging

class DefaultLogger:

    def __init__(self):
        self._formatter = logging.Formatter(logging.BASIC_FORMAT)
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.DEBUG)
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(self._formatter)
        self._logger.addHandler(sh)

class Logger:

    def __init__(self):
        self._logger = logging.getLogger()

    def act_as_main(self):
        # self._formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s: %(message)s')



    def add_to_chain(self):
        pass

    def _format_message(self, message):
        pass

    def debug(self, msg):
        self._logger.debug(msg)


class Parent:
    log = Logger()
    def __init__(self):
        self.log.debug('This is parent')
        self.some_list = []


class Child:
    log = Logger()
    def __init__(self, parent):
        self.parent = parent
        self.log.debug('This is child')


class SomeClass:
    log = Logger()
    def __init__(self):
        self.log.debug('This is some class')

#l = Logger(True)
#l.debug('This is main logger')
#p = Parent()
#c = Child(p)
#s = SomeClass()
