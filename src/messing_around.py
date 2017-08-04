# Copyright (c) Peter Majko.

from rhapsody.io.human_input import ConsoleInputConverter

if __name__ == '__main__':
    cic = ConsoleInputConverter()
    cic.convert(input('~ '))
