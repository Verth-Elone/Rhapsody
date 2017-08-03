# Copyright (c) Peter Majko.

"""
Rhapsody's TCP Server based on Twisted
"""
from rhapsody.io.log import get_default_logger
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory, Protocol, connectionDone
from twisted.protocols.policies import TimeoutMixin

from sys import maxsize

from struct import pack, unpack

import json


class TCPServer:
    """
    TCPServer instance is meant to be run in a separate process
    """
    def __init__(self, interface='localhost', port=5555,
                 encoding='UTF-8', timeout=300, logger_name='TCPServer'):
        self.log = get_default_logger(logger_name)
        self._reactor = reactor
        self._endpoint = TCP4ServerEndpoint(reactor=self._reactor, port=port, interface=interface)
        self._endpoint.listen(MainFactory(self))
        self.encoding = encoding
        self.timeout = timeout

    def start(self):
        self._reactor.run()

    def stop(self):
        self._reactor.stop()


class MainFactory(Factory):
    def __init__(self, parent: TCPServer):
        self.parent = parent

    def buildProtocol(self, addr):
        return MainProtocol(self.parent)


class MainProtocol(Protocol, TimeoutMixin):

    total_data = b''
    remaining_data = b''
    data_len = maxsize

    def __init__(self, parent: TCPServer):
        self.parent = parent
        self.engineer = None
#        self.logger = None

    def connectionMade(self):
        c_ip, c_port = self.transport.client
#        logger_name = '{pln}.Protocol({cip})'.format(pln=self.parent.logger.name, cip=c_ip)
#        self.logger = logging.getLogger(logger_name)
#        self.logger.debug('Client connected')
        self.setTimeout(self.parent.timeout)
#        # Create new client engineer
#        self.engineer = Engineer(self)
#        # Add the engineer to AppServer's engineers collection
#        self.parent.parent.engineers.append(self.engineer)
#        # self.send_data('{"TEXT":"Hello there Mr. Client :)"}')
#        # TODO: LATE PHASE> Send a key to the client to encode the messages based on it

    def dataReceived(self, data):
        self.resetTimeout()
        self.logger.debug('Data chunk: {}'.format(data))
        self.total_data = self.remaining_data + data
        while self.total_data:
            if len(self.total_data) > 4:
                self.data_len = unpack('>i', self.total_data[:4])[0]
                # self.logger.debug('Data package length: {}'.format(self.data_len))
                if len(self.total_data[4:]) >= self.data_len:
                    msg = self.total_data[4:self.data_len+4]
                    self.logger.debug('Data package msg: {}'.format(msg))
                    # COMMAND EXECUTION START
                    try:
                        cmd_list = json.loads(str(msg, self.parent.encoding))
                    except Exception as ex:
                        self.logger.error("Incorrect format of command: {}".format(str(msg, self.parent.encoding)))
                        self.transport.loseConnection()
                    else:
                        self.logger.debug('Pushing CMD: {}'.format(str(cmd_list)))
                        if len(cmd_list) == 2:
                            result = self.engineer.do(cmd_list[0], cmd_list[1])
                            self.logger.debug('Sending back result: {}'.format(str(result)))
                            self.send_msg('response', result)
                        else:
                            self.logger.error("Incorrect number of elements in list: {}".format(str(cmd_list)))
                            self.transport.loseConnection()
                    # COMMAND EXECUTION END
                    # add rest of the data to the total_data, if any
                    self.total_data = self.total_data[self.data_len+4:]
                else:
                    self.remaining_data = self.total_data
                    self.total_data = b''
            else:
                self.remaining_data = self.total_data
                self.total_data = b''

    def connectionLost(self, reason=connectionDone):
#        self.logger.debug('Connection Lost: {reason}'.format(reason=connectionDone.value))
        pass

    def timeoutConnection(self):
#        self.logger.debug('Connection Timeout')
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
        self.logger.debug('Data sent')
