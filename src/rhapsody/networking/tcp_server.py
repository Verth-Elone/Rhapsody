# Copyright (c) Peter Majko.

"""
Rhapsody's TCP Server based on Twisted
"""
from rhapsody.io.log import get_default_logger, get_child_logger, LoggingPipeHandler
from rhapsody.core.command import CommandProcessor
from rhapsody.networking.handler import TwistedPipeHandler

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import ServerFactory, Protocol, connectionDone
from twisted.protocols.policies import TimeoutMixin

from sys import maxsize

from struct import pack, unpack

import json


class TCPServer:
    """
    TCPServer
    """
    def __init__(self, interface='localhost', port=5555,
                 encoding='utf8', timeout=300, logger_name='TCPServer'):
        """

        :param interface: str
        :param port: int
        :param encoding: str
        :param timeout: int
        :param logger_name: str
        """
        self.interface = interface
        self.port = port
        self.log = get_default_logger(logger_name)
        self._reactor = reactor
        self._endpoint = TCP4ServerEndpoint(reactor=self._reactor, port=self.port, interface=self.interface)
        self._endpoint.listen(MainFactory(self))
        self.encoding = encoding
        self.timeout = timeout

    def start(self):
        self.log.info('TCP Server running at {ip}:{p}'.format(ip=self.interface, p=self.port))
        self._reactor.run()

    def stop(self):
        self._reactor.stop()


class PTCPServer(TCPServer):
    """
    TCPServer meant to run in separate process. PTCPServer means PipedTCPServer :)
    """
    def __init__(self, pipe_conn, interface='localhost', port=5555,
                 encoding='utf8', timeout=300, logger_name='PTCPServer'):
        """
        PTCPServer should be initialized in separate process from main process.
        pipe_conn is a must - it is a connection endpoint for pipe to main process
        :param pipe_conn: multiprocessing.Connection
        :param interface: str
        :param port: int
        :param encoding: str
        :param timeout: int
        :param logger_name: str
        """
        super().__init__(interface=interface, port=port, encoding=encoding, timeout=timeout, logger_name=logger_name)
        self.parent_process_conn = pipe_conn
        self.log.debug('Registering parent process pipe handler.')
        self.parent_process_pipe_handler = TwistedPipeHandler(self.parent_process_conn)
        self.log.debug('Creating logging pipe handler.')
        lph = LoggingPipeHandler(self.parent_process_pipe_handler, 'DEBUG')
        lph.setFormatter(self.log.handlers[0].formatter)
        self.log.debug('Adding logging pipe handler.')
        self.log.addHandler(lph)
        self.log.debug('Logging pipe handler successfully initialized.')


class MainFactory(ServerFactory):
    def __init__(self, parent: TCPServer):
        self.parent = parent

    def buildProtocol(self, addr):
        protocol = MainProtocol(self.parent)
        return protocol


class MainProtocol(Protocol, TimeoutMixin):

    total_data = b''
    remaining_data = b''
    data_len = maxsize

    def __init__(self, parent: TCPServer):
        """
        :param parent: TCPServer
        """
        self.parent = parent
        self.log = None
        self.command_processor = None
        self.commands = {}

    def connectionMade(self):
        """
        Initialize self.log (logger) with the ip address of client
        :return:
        """
        client_ip, client_port = self.transport.client
        self.log = get_child_logger(self.parent.log, 'Protocol({})'.format(client_ip))
        self.log.debug('Client connected')
        self.command_processor = CommandProcessor(self.commands, get_child_logger(self.log, 'CommandProcessor'))
        self.setTimeout(self.parent.timeout)
        # self.send_msg('RESPONSE', '{"TEXT":"Hello there Mr. Client :)"}')

    def dataReceived(self, data):
        self.resetTimeout()
        self.log.debug('Data chunk: {}'.format(data))
        self.total_data = self.remaining_data + data
        while self.total_data:
            if len(self.total_data) > 4:
                self.data_len = unpack('>i', self.total_data[:4])[0]
                self.log.debug('Data package length: {}'.format(self.data_len))
                if len(self.total_data[4:]) >= self.data_len:
                    msg = self.total_data[4:self.data_len+4]
                    self.log.debug('Data package msg: {}'.format(msg))
                    # decode b msg to s msg
                    decoded_msg = str(msg, self.parent.encoding)
                    # region Command Processing
                    try:
                        result = self.command_processor.process(decoded_msg)
                    except Exception as ex:
                        # this is a broad exception, but we don't want the code to fail here ;)
                        self.log.error("Exception during command processing: {}".format(ex))
                        self.transport.loseConnection()
                    else:
                        self.log.debug('Sending back result: {}'.format(str(result)))
                        self.send_msg('response', result)
                    # endregion
                    # add rest of the data to the total_data, if any
                    self.total_data = self.total_data[self.data_len+4:]
                else:
                    self.remaining_data = self.total_data
                    self.total_data = b''
            else:
                self.remaining_data = self.total_data
                self.total_data = b''

    def connectionLost(self, reason=connectionDone):
        self.log.debug('Connection Lost: {reason}'.format(reason=connectionDone.value))

    def timeoutConnection(self):
        self.log.debug('Connection Timeout')
        self.transport.abortConnection()

    def send_msg(self, msg_type, msg_data):
        msg = dict()
        msg['TYPE'] = msg_type
        msg['DATA'] = msg_data
        json_msg = json.dumps(msg)
        enc_message = bytes(str(json_msg), self.parent.encoding)
        enc_message_len = pack('>i', len(enc_message))
        package = enc_message_len + enc_message
        self.transport.write(package)
        self.log.debug('Data sent')
