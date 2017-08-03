# Copyright (c) Peter Majko.

"""
Rhapsody's core.command module
"""
from rhapsody.io.log import get_default_logger
from rhapsody.core.exceptions import UnsupportedDataType, UnsupportedDataInterchangeFormat
import json
import xml


class CommandProcessor:
    # TODO: Proper commenting

    def __init__(self, commands: dict, logger=None):
        if not logger:
            logger = get_default_logger('CommandProcessor')
        self.log = logger
        self.commands = commands
        self.data = None

    def process(self, data):
        self.log.debug('Data {} {}'.format(type(data), data))
        command_name, args, kwargs = self.resolve_data(data)
        return self._call_command(command_name, args, kwargs)

    def resolve_data(self, data):
        """
        Tries to make sense out of data :)
        :type data: json, xml(not yet implemented) string
                    OR data structure object as tuple, list or dict(not yet implemented)
        :return: tuple (command_name, args, kwargs)
        """

        # First if the data is a string, try to convert it to a data structure
        if isinstance(data, str):
            # try to determine the data structure out of string
            data_structure = self.try_json(data)
            if not data_structure:
                data_structure = self.try_xml(data)
            if not data_structure:
                raise UnsupportedDataInterchangeFormat(data, ['json', 'xml'])
        else:
            # else suppose that data itself is a data structure
            data_structure = data

        # Then the data should be of type tuple, list or dict
        # At the moment dict is not supported!
        if isinstance(data_structure, tuple) or isinstance(data_structure, list):
            command_name = data_structure[0]
            try:
                args = data_structure[1]
            except IndexError:
                args = []
            try:
                kwargs = data_structure[2]
            except IndexError:
                kwargs = {}
            return command_name, args, kwargs
        else:
           raise UnsupportedDataType('data_structure', data_structure, [list, tuple])

    def try_json(self, data):
        """
        Try to convert data to data structure
        :param data:
        :return:
        """
        try:
            data_struct = json.loads(data)
        except json.decoder.JSONDecodeError as err:
            self.log.debug('Data not a json struct. Err: {}'.format(err))
            return None
        else:
            self.log.debug('Data is a json struct')
            return data_struct

    def try_xml(self, data):
        """

        :param data:
        :return:
        """
        # TODO - implement try_xml
        self.log.debug('Data not an XML struct - perhaps yet, but not implemented :D')
        return None

    def _call_command(self, command_name, args, kwargs):
        """
        Shouldn't be called directly, only through process method
        :param command_name:
        :param args:
        :param kwargs:
        :return: return value of the func/method called
        """
        try:
            response = self.commands[command_name](*args, **kwargs)
        except KeyError as err:
            self.log.error('Attempt to call invalid command ({})'.format(err))
            raise err
        else:
            return response
