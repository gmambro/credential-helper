from subprocess import call
import logging

def start_agent(self):
    logging.debug("Starting agent")
    
    try:
        status = call(['credentialcache-agent', socket_path])
    except OSError as e:
        status = call(['python', '-m', 'credentialcache.agent' ])

    logging.debug("started with status=%d", status)
    return status




