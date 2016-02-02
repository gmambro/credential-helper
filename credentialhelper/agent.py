"""The credential cache agent."""
import os
from os import path
import sys
import atexit
import logging
import signal
from optparse import OptionParser

from credentialhelper import Server, Config


class Agent(object):

    def __init__(self, argv):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
               
        self.server = None
        self.config = None

    def execute(self):
        """Main entry point for the agent."""

        usage = 'credentialcache-agent [options]'
    
        parser = OptionParser(usage=usage)
        parser.add_option("-c", "--config-dir",
                          dest="config_dir",
                          metavar="DIRECTORY",
                          help="configuration directory")
        (options, args) = parser.parse_args(self.argv)
        
        config = Config(options.config_dir)
        self.config = config
        
        self.check_socket_path()
        
        server = Server(config)
        self.server = server
        
        atexit.register(self.on_close)
        signal.signal(signal.SIGTERM, self.sig_handler)
        
        server.listen()    
        try:
            server.loop()
        except KeyboardInterrupt as e:
            server.close()
    
        sys.exit(0)
    
    def check_socket_path(self):
        """Check directory permission and create it if needed"""

        socket_path = self.config.get_socket_path()
        dir_name = path.dirname(socket_path)

        if not os.path.exists(dir_name):
            # create parent dirs if needed but do not create the socket
            # dir in order to set permissions while creating
            parent_dir = path.dirname(dir_name)
            if parent_dir != '' and not path.exists(parent_dir):
                os.makedirs(parent_dir)
            os.mkdir(dir_name, 0700)
        else:
            dir_info = os.stat(dir_name)
            if dir_info.st_mode & 077:
                print >>sys.stderr, ("%s must be 700" % dir_name)
                sys.exit(1)

    def sig_handler(self, signal, frame):
        sys.exit(0)
            
    def on_close(self):
        if self.server:
            self.server.close()
    

                
def execute_from_command_line(argv=None):
    """
    A simple method that runs an Agent.
    """
    agent = Agent(argv)
    agent.execute()
