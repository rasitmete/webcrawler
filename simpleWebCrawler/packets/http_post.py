__author__ = "rasitmete"    


from simpleWebCrawler.packets.packet import Packet
from simpleWebCrawler.http_utility import HTTP_VERSION
from simpleWebCrawler.http_utility import CRLF
from simpleWebCrawler.http_utility import Utility
    
class HttpPost(Packet):    
    """Http Get packets
        
    """
    Method_Name = "POST"

    def __init__(self, hostname, url, csrf_token, session_id, params):
        self._hostname = hostname
        self._url = url
        self._csrf_token = csrf_token
        self._session_id = session_id
        self._params = params

    def form_packet(self):
        """[This will form a POST request and to send to the http://cs5700f18.ccs.neu.edu/fakebook/{number}, port: 80 with TCP ]
        
        Returns:
            [str] -- [fromed HTTP POST packet]
        """
        content = Utility.url_encode(self._params)
        Request = HttpPost.Method_Name + " " + self._url + " " + HTTP_VERSION 

        data  = Request + CRLF
        data += "Host:" + " " + self._hostname + CRLF
        data += "Content-Length: "+ str(len(content)) + CRLF
        data += "Content-Type: application/x-www-form-urlencoded" + CRLF
        data += "Cookie: csrftoken={}; sessionid={}".format(self._csrf_token, self._session_id) + CRLF
        data += "Connection: keep-alive" + CRLF
        data += CRLF
        data = data.encode('ascii')

        data = data + content

        return data
