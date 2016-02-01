import logging

class BaseProtocolHandler(object):

    def read_stanza(self, fh):
        request = dict()
        
        while True:
            logging.debug( "waiting line")
            l = fh.readline().rstrip('\r\n')
            
            if l == '' or l == '\n':
                logging.debug( "received end of stanza")
                break
        
            logging.debug("received: %s", l)
            (k,sep, v) = l.partition('=')

            if sep is None:
                return None
        
            request[k] = v
        
        return request

    def write_stanza(self, fh, data):
        for (key, value) in data.iteritems():
            print >>fh, "%s=%s" % (key, value)            
        print >>fh, ""
        fh.flush()
