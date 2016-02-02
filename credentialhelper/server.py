import errno
import socket
import logging
import time

from weakref import WeakValueDictionary
from protocol import BaseProtocolHandler

import os

class CacheEntry(object):

    def __init__(self, username, password, expire=None):
        self.username = username
        self.password = password
        self.expire   = expire
        
class Cache(object):

    def __init__(self, config):
        self._entries = dict()

        # indexed by (domain, user) tuple
        self._entry_by_domain = WeakValueDictionary()

        self._config = config

    def set(self, service, username, password, timeout=None):
        expire = None
        if timeout:
            expire = int(time.time()) + timeout
            
        entry = CacheEntry(username, password, expire)
        self._entries[service] = entry

        domain = self._config.get_domain_for_service(service) 
        if domain is not None:
            logging.debug("updating password for domain,user = %s,%s", domain, username)
            self._entry_by_domain[(domain, username)] = entry

    def get(self, service):
        entry = self._entries.get(service)
        if entry is None:
            domain   = self._config.get_domain_for_service(service)
            username = self._config.get_user_for_service(service)

            if domain and username:
                logging.debug("searching in domain %s", domain)
                entry = self._entry_by_domain.get((domain, username))
                
        if entry is None:
            return None

        now = int(time.time())
        if entry.expire and entry.expire <= now:
            del self._entries[service]
            # no need to delete from domain dict since is a weakref values
            return None
        
        return entry
            
class Server(BaseProtocolHandler):

    def __init__(self, config):
        self._socket_path = config.get_socket_path()
        self._sock = None
        self._do_loop = True
        self._cache = Cache(config)
        self._config = config

    def listen(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        socket_path = self._socket_path
        if os.path.exists(socket_path):
            os.unlink(socket_path)
        sock.bind(socket_path)
        sock.listen(1)
        self._sock = sock
        
    def loop(self):
        sock = self._sock
        while self._do_loop:
            connection, client_address = sock.accept()

            try:
                f = connection.makefile()
                logging.debug( "client connected" )
                request = self.read_stanza(f)

                if request is None:
                    continue
                
                action = request.get('action')
                if action:
                    logging.debug( "action = %s", action )
                    handler = getattr(self, "handle_%s" % action, self.handle_unkwown)
                    handler(f, request)
                else:
                    logging.error("no action in request")
                
            finally:
                connection.close()

        self.close()

    def handle_exit(self, fh, request):
        self.do_loop = False

    def handle_unkwown(self, fh, request):
        action = request.get('action')
        logging.error("Unknown action %s", action)
        
    def handle_get(self, fh, request):
        service = request.get('service')
        
        entry = self._cache.get(service)

        response = dict()
        response['service'] = service
        if entry:
            response['username'] = entry.username
            response['password'] = entry.password
        else:
            default_username = self._config.get_user_for_service(service)
            if default_username:
                logging.debug('setting default username for service')
                response['username'] = default_username

            
        self.write_stanza(fh, response)

    def handle_set(self, fh, request):
        response = dict()

        try:
            service  = request['service']
            username = request['username']
            password = request['password']
            timeout  = request.get('timeout')

            if service:
                logging.debug("updating service %s", service)
                self._cache.set(service, username, password, timeout)        
                response['status'] = 'OK'
        finally:
            if not 'status' in response:
                response['status'] = 'Error'
        
        self.write_stanza(fh, response)           
        
    def close(self):
        if self._sock:
            self._sock.close()
            self._sock = None

        # clean up socket file
        if os.path.exists(self._socket_path):
            os.unlink(self._socket_path)
