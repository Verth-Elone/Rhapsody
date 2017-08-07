# Copyright (c) Peter Majko.

"""
Rhapsody: Rapid Heterogeneous Applications Development Framework.
"""
from rhapsody.io.log import get_default_logger

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError, InternalError


class Database:

    connection_string_templates = {
        'psql': 'postgresql+psycopg2://{user}:{pswd}@{host}/{db_name}',
        'mssql': 'mssql+pyodbc://{user}:{pswd}@{host}/{db_name}?driver=SQL+Server'
    }

    def __init__(self, name, type_, host, user, pswd, logger=None):
        if not logger:
            logger = get_default_logger('{}({})'.format(self.__class__.__name__, name))
        self.log = logger
        self.name = name
        self.type = type_
        self.host = host
        self.user = user
        self.pswd = pswd
        connection_string = self.connection_string_templates[self.type].format(user=self.user, pswd=self.pswd,
                                                                               host=self.host, db_name=self.name)
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)  # Not thread safe!
        # Use below for the thread safe Session. class!
        # self.session_factory = sessionmaker(bind=self.engine)
        # self.Session = scoped_session(self.session_factory)

    def get_session(self):
        """Don't forget to close the session!!!"""
        return self.Session()
    
    def create_self(self, super_user_database, overwrite=False):
        super_session = super_user_database.get_session()
        super_session.execute('COMMIT')

        if overwrite:
            # destroy database
            super_session.execute('DROP DATABASE IF EXISTS {};'.format(self.name))
            super_session.execute('COMMIT')

        try:
            # create databases
            super_session.execute('CREATE DATABASE {0} OWNER {1};'.format(self.name, self.user))
            super_session.execute('COMMIT')
        except ProgrammingError as err:
            self.log.warn('CREATE DATABASE not successful: {}'.format(err))
            return -2
        finally:
            super_session.close()

    def create_tables_from_orm_dict(self, orm_dict):
        for setup in orm_dict:
            cls = setup['class']
            self.log.debug('Creating table for ORM class {c} with name: {t}'.format(c=cls.__name__,
                                                                                    t=cls.__tablename__))
            cls.metadata.create_all(self.engine)

    def fill_from_orm_dict(self, orm_dict):
        """
        See rhapsody.database.example_orm_dict for more info.
        :param orm_dict: dict
        :return: -
        """
        self.log.debug('Filling database with data from orm dictionary')
        session = self.get_session()
        try:
            for setup in orm_dict:
                setup_class = setup['class']  # pointer to the class
                self.log.debug(setup_class.__tablename__ + ': ')
                setup_data = setup['data']
                for record in setup_data:
                    self.log.debug(record)
                    instance = setup_class(**record)  # create object from the class
                    try:
                        # 1-N, N-1, N-N relations
                        children = instance.get_children()
                    except AttributeError as err:
                        pass
                    else:
                        for child in children:
                            session.add(child)
                    session.add(instance)
                    session.commit()
        finally:
            session.close()


class DatabaseUser(Database):

    def __init__(self, name, pswd, type_, host, logger=None):
        super().__init__(name, type_, host, name, pswd, logger)

    def create_self(self, super_user_database, overwrite=False):
        super_session = super_user_database.get_session()
        super_session.execute('COMMIT')

        if overwrite:
            # drop user
            try:
                super_session.execute('DROP USER IF EXISTS {0};'.format(self.name))
                super_session.execute('COMMIT')
            except InternalError as err:
                self.log.warn('(Err: {}).'.format(err))
                return -3

        # create user
        try:
            super_session.execute('CREATE USER {0} WITH PASSWORD \'{1}\';'.format(self.name, self.pswd))
            super_session.execute('COMMIT')
        except ProgrammingError as err:
            self.log.warn('CREATE USER not successful: {}'.format(err))
            return -1
        else:
            # create user's main database - same db name as user name
            try:
                super_session.execute('CREATE DATABASE {0} OWNER {0};'.format(self.name))
                super_session.execute('COMMIT')
            except ProgrammingError as err:
                self.log.warn('CREATE DATABASE not successful: {}'.format(err))
                return -2
