# Copyright (c) Peter Majko.

"""
Rhapsody: Rapid Heterogeneous Applications Development Framework.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Database:

    def __init__(self, name, connection_string):
        self.name = name
        self.connection_string = connection_string
        self.engine = create_engine(self.connection_string)
        self.Session = sessionmaker(bind=self.engine)  # Not thread safe!
        # Use below for the thread safe Session. class!
        # self.session_factory = sessionmaker(bind=self.engine)
        # self.Session = scoped_session(self.session_factory)

    def get_session(self):
        """Don't forget to close the session!!!"""
        return self.Session()
