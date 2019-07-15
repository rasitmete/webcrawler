__author__ = "rasitmete"

from simpleWebCrawler.packets.packet import Packet
from simpleWebCrawler.http_utility import HTTP_VERSION
from simpleWebCrawler.http_utility import CRLF



class HttpGet(Packet):
    
    """Http Get packets
    
    """

    Method_Name = "GET"


    def __init__(self, hostname, url, csrf_token=None, session_id=None):
        self._hostname = hostname
        self._url = url
        self._csrf_token = csrf_token
        self._session_id = session_id

    
    def form_packet(self):
        """[This will form a GET request and before sending to the http://cs5700f18.ccs.neu.edu/fakebook/{number}, port: 80 with TCP ]
        
        Returns:
            [str] -- [fromed HTTP GET packet]
        """
        Request = HttpGet.Method_Name + " " + self._url + " " + HTTP_VERSION 

        data = Request + CRLF
        data += "Host:" + " " + self._hostname + CRLF
        if not self._csrf_token == None:
            data += "Cookie: csrftoken={}".format(self._csrf_token)
        if not self._session_id == None:
            data += "; sessionid={}".format(self._session_id)
        
        if not self._csrf_token == None or not self._session_id == None:
            data+= CRLF
        data += "Connection: keep-alive" + CRLF
        data += CRLF
        data = data.encode('ascii')
        
        return data        

