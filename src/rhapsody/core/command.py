# Copyright (c) Peter Majko.

"""

"""


class CommandProcessor:

    def __init__(self, commands: dict):
        self.commands = commands
        self.data = None

    def process(self, data):
        command_name, args, kwargs = self.resolve_data(data)
        return self._call_command(command_name, args, kwargs)

    def resolve_data(self, data):
        """
        Should check if data are ok. Overload, but always return tuple of 3
        :return: tuple (command_name, args, kwargs)
        """
        command_name = data[0]
        try:
            args = data[1]
        except IndexError:
            args = []
        try:
            kwargs = data[2]
        except IndexError:
            kwargs = {}
        return command_name, args, kwargs

    def _call_command(self, command_name, args, kwargs):
        response = self.commands[command_name](*args, **kwargs)
        return response


def t_func(x, y, z=1):
    print(x*y*z)

if __name__ == '__main__':
    cmds = {
        'p': print,
        't': t_func
    }
    cp = CommandProcessor(cmds)

    tl = [
        None,
        ['p'],
        ['p', 'hello'],
        ['p', ['hello']],
        ['t', [None, 2]]
    ]

    cp.process(tl[4])
    cp.process(tl[3])

