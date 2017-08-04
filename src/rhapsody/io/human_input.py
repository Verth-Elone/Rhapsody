# Copyright (c) Peter Majko.

"""
Rhapsody: Rapid Heterogeneous Applications Development Framework.
"""

from re import compile as regex_compile
from rhapsody.io.log import get_default_logger


class ConsoleInputConverter:
    _INPUTPATTERN = regex_compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
    _INPUTPATTERN2 = regex_compile(r'''(["]*["]|[']*['])''')

    def __init__(self, logger=None):
        if not logger:
            logger = get_default_logger(self.__class__.__name__)
        self.log = logger

    def convert(self, user_input: str, to_type='OBJECT'):
        if len(user_input) < 1:
            self.log.debug('User input is empty!')
            return False
        else:
            input_list = self._INPUTPATTERN.split(user_input)
            if len(input_list) < 2:
                self.log.debug('Invalid input!')
                return False
            if input_list[1] in ['p', 'parent', self.parent.name]:
                commands = self.parent.commands
                i = 3
            else:
                commands = self.commands
                i = 1
            if len(input_list) < i + 1:
                self.logger.info('No command given!')
                continue
            # user_command = input_list[i]
            # user_params = []
            # for element in input_list[i + 1:]:
            #     element_list = self._INPUTPATTERN.split(element)
            #     for e in element_list:
            #         if not e in ['', '\'', '"', ' ']:
            #             if e == 'True':
            #                 e = True
            #             elif e == 'False':
            #                 e = False
            #             elif (e[0] == '"' and e[-1] == '"') or (e[0] == "'" and e[-1] == "'"):
            #                 # to get rid of quotes for SQL statements or so :)
            #                 e = e[1:-1]
            #             else:
            #                 e = e
            #             user_params.append(e)
            # # check if the supported input matches any command
            # if user_command in commands:
            #     # check if the command (function, method) supports parameters
            #     cmd_signature = signature(commands[user_command])
            #     cmd_params = cmd_signature.parameters
            #     # check if user has not specified more parameters than command can take
            #     if len(user_params) <= len(cmd_params):
            #         # check if there are any parameters required at all
            #         if bool(cmd_params):
            #             # check how many parameters are non-optional (no default value)
            #             count_of_req_params = [(lambda param: param.default is param.empty)(cmd_params[p])
            #                                    for p in cmd_params].count(True)
            #             # check if user provided enough non-optional parameters
            #
            #             if count_of_req_params <= len(user_params):
            #                 # finally run the command :)
            #
            #                 commands[user_command](*user_params)
            #             else:
            #                 self.logger.info('Too few parameters. Command "{c}" takes {l} parameters: {p}'.format(
            #                     c=user_command,
            #                     l=len(cmd_params),
            #                     p=str(cmd_signature)))
            #         else:
            #             commands[user_command]()
            #     else:
            #         self.logger.info('Too many parameters. Command "{c}" takes {l} parameters: {p}'.format(
            #             c=user_command,
            #             l=len(cmd_params),
            #             p=str(cmd_signature)))
            # else:
            #     self.logger.info('Invalid command')
            #     self.logger.info('Available Console commands: {cc}'.format(cc=con_cmd_lst))
            #     self.logger.info('Available {pn} commands: {pc}'.format(pn=self.parent.name, pc=par_cmd_lst))
