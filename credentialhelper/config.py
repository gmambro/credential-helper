from os import path
import ConfigParser

class Config(object):

    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = path.expanduser("~/.credentialhelper")            
        self._config_dir = config_dir

        config = ConfigParser.ConfigParser()
        config.read(path.join(self._config_dir, "config"))
        self._config = config
            
    def get_socket_path(self):
        return path.join(self._config_dir, "socket");

    def _get_service_value(self, service, option):
        section = "service %s" % service

        try:
            return self._config.get(section, option)
        except ConfigParser.NoSectionError:
            return None

    def get_user_for_service(self, service):
        return self._get_service_value(service, "user")

    def get_domain_for_service(self, service):
        return self._get_service_value(service, "domain")

