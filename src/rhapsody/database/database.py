# Copyright (c) Peter Majko.

"""
Rhapsody: Rapid Heterogeneous Applications Development Framework.
"""
from sqlalchemy import create_engine


class Database:

    def __init__(self, name, connection_string):
        self.name = name
        self.connection_string = connection_string
        self.engine = create_engine(self.connection_string)
