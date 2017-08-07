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
    def __init__(self, protocol_factory_class, interface='localhost', port=5555,
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
        self._endpoint.listen(protocol_factory_class(self))
        self.encoding = encoding
        self.timeout = timeout

    def start(self):
        self.log.info('TCP Server running at {ip}:{p}'.format(ip=self.interface, p=self.port))
        self._reactor.run()

    def stop(self):
        self.log.info('Stopping reactor...')
        self._reactor.stop()
        self.log.info('Reactor stopped.')


class PTCPServer(TCPServer):
    """
    TCPServer meant to run in separate process. PTCPServer means PipedTCPServer :)
    """
    def __init__(self, pipe_conn, protocol_factory_class, interface='localhost', port=5555,
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
        super().__init__(protocol_factory_class=protocol_factory_class,
                         interface=interface, port=port, encoding=encoding, timeout=timeout, logger_name=logger_name)
        # connect this side of pipe
        self.parent_process_conn = pipe_conn
        # CommandProcessor to process commands sent by other side of pipe
        self.command_processor = CommandProcessor({'stop': self.stop}, self.log)
        # create the handler for process to process pipe
        self.parent_process_pipe_handler = TwistedPipeHandler(pipe_conn=self.parent_process_conn,
                                                              on_recv_handle=self.handle_command)
        # create handler for logging, so all logging goes to the other side of pipe
        lph = LoggingPipeHandler(self.parent_process_pipe_handler, 'DEBUG')
        lph.setFormatter(self.log.handlers[0].formatter)
        # replace the default StreamHandler with LoggingPipeHandler
        # in the case both should be kept, use self.log.addHandler(lph) instead
        self.log.handlers[0] = lph

    def handle_command(self, data):
        """
        Tries to process the data received from the other side of connection.
        Refer to rhapsody.core.command.CommandProcessor for more information.
        :param data: data received from the other side of pipe, can be anything
        :return: -
        """
        try:
            self.command_processor.process(data)
        except Exception as err:
            self.log.warning('Command handling not successful. Err: {}'.format(err))


class MainFactory(ServerFactory):
    """
    Just a factory.
    """
    def __init__(self, parent: TCPServer):
        self.parent = parent

    def buildProtocol(self, addr):
        protocol = MainProtocol(self.parent)
        # TODO register commands with the protocol!
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

    def connectionMade(self):
        """
        Initialize self.log (logger) with the ip address of client.
        Initialize self.command_processor with self.commands
        :return: -
        """
        client_ip, client_port = self.transport.client
        self.log = get_child_logger(self.parent.log, 'Protocol({})'.format(client_ip))
        self.log.debug('Client connected')
        self.setTimeout(self.parent.timeout)

    def dataReceived(self, data):
        """
        Process data which were sent by client.
        :param data: bytes
        :return: -
        """
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
                    # do something with the message
                    self.msg_handle(decoded_msg)
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
        # create message out of msg_type and msg_data, this should always be 2 element list
        msg = [msg_type, msg_data]
        # transform to json
        json_msg = json.dumps(msg)
        # transform json string message to bytes
        enc_message = bytes(str(json_msg), self.parent.encoding)
        # get the 4 bytes long header for the message - how many bytes are in the message
        enc_message_len = pack('>i', len(enc_message))
        # join header and message together
        package = enc_message_len + enc_message
        # send to client
        self.transport.write(package)
        self.log.debug('Data sent')

    def msg_handle(self, decoded_msg):
        """
        Meant for override - do anything with the message here.
        :param decoded_msg: string
        :return: -
        """
        self.log.debug('Processing message: {}'.format(decoded_msg))
        try:
            result = None
        except Exception as ex:
            # this is a broad exception, but we don't want the code to fail here ;)
            # client will be disconnected
            self.log.error("Exception during command processing: {}".format(ex))
            self.transport.loseConnection()
        else:
            self.log.debug('Sending back result: {}'.format(str(result)))
            self.send_msg('r', result)  # 'r' means response
