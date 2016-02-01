"""The client for the cache agent"""
import errno
import socket
import logging
from .protocol import BaseProtocolHandler

class ConnectionRefusedException(Exception):
    pass

class Client(BaseProtocolHandler):

    def __init__(self, config):
        self._socket_path = config.get_socket_path()
        self._sock = None
       
        
    def connect(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening        
        logging.debug("connecting to %s")
        try:
            sock.connect(self._socket_path)            
        except socket.error as error:
            # this allows agent autostart
            if error.errno in (errno.ENOENT,  errno.ECONNREFUSED):                
                raise ConnectionRefusedException()
            else:
                raise

        self._sock = sock
        
    def get(self, service):
        req = {
            'action'  : 'get',
            'service' : service
        }
        return self.send_request(req)

    def set(self, service, username, password):
        req = {
            'action'   : 'set',
            'service'  : service,
            'username' : username,
            'password' : password,
        }
        return self.send_request(req)

    def send_request(self, request):
        sock = self._sock
        f = sock.makefile()
        
        self.write_stanza(f, request)
        return self.read_stanza(f)
        

    def close(self):
        if self._sock:
            self._sock.close()

