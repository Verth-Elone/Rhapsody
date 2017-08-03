# Copyright (c) Peter Majko.

"""
Rhapsody: Rapid Heterogeneous Applications Development Framework.
"""


class UnsupportedDataType(Exception):
    def __init__(self, pointer_name, pointer, supported_data_types=None):
        message = '"{}" is of type {}. Supported types: {}'.format(pointer_name,
                                                                   type(pointer),
                                                                   supported_data_types)
        super().__init__(message)


class UnsupportedDataInterchangeFormat(Exception):
    def __init__(self, pointer_name, supported_formats=None):
        message = '"{}" is of unknown data interchange format. Supported types: {}'.format(
            pointer_name, supported_formats)
        super().__init__(message)
