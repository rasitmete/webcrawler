__author__ = "rasitmete"

CRLF = "\r\n"
HTTP_VERSION = "HTTP/1.1"
RECV_BUFFER_SIZE = 4096
DEBUG_FLAG = 1

class Utility():

    @staticmethod
    def url_encode(params):
        """This module provides the constant variables of and the utility functions
        Arguments:
            params {[dict]} -- Post Message parameters packed with URL encoding
        
        Raises:
            ValueError -- If the parameters are not in dictionary, raise error
        
        Returns:
            [str] -- packed parameters as a single string
        """
        if hasattr(params, 'items'):
            params = params.items()
            l = [str(key)+"="+str(value) for key,value in params]
            return '&'.join(l).encode('ascii')
        else: 
            raise ValueError("parameters should be dictionary")
