from subprocess import call
import logging
import sys

from .client import Client, ConnectionRefusedException


def start_agent(self):
    logging.debug("Starting agent")
    
    try:
        status = call(['credentialhelper-agent'])
    except OSError as e:
        status = call(['python', '-m', 'credentialhelper.agent' ])

    logging.debug("started with status=%d", status)
    return status

def fetch_credentials(service, config=None):
    """Return a (username, password, stored) tuple"""
    client = Client(config)
    try:
        client.connect()
    except ConnectionRefusedException:
        logging.debug("Starting agent");
        start_agent(config.get_socket_path())
        client.connect()
        
    res = client.get(service)
    client.close()

    stored = True
    
    username = res.get('username')
    if username is None:
        username = ask_username()
        stored = False
    password = res.get('password')
    if password is None:
        password = ask_password()
        stored = False

    return (username, password, stored)
    
def ask_password():
    import getpass
    print >>sys.stderr, "Password: ",
    return getpass.getpass('')

def ask_username():
    print >>sys.stderr, "Username: ",
    return raw_input()

    


