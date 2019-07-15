__author__ = "rasitmete"

from simpleWebCrawler.packets.packet import Packet
from simpleWebCrawler.packets.http_status import HttpStatus
from simpleWebCrawler.http_utility import HTTP_VERSION
from simpleWebCrawler.http_utility import CRLF
from simpleWebCrawler.http_utility import DEBUG_FLAG


class HttpResponse(Packet):
    """This class is responsible for the respnse message acquired
    """
    def __init__(self, data):
        
        self._isValid = True
        if not HttpResponse.initial_response_check(data):
            self._isValid = False

        self._data = data
        self._parsed_response = {}

        self.parse_response()

    def parse_response(self):
        """ This method parses the response data received from the server.
        """
        status_line = self._data.split(CRLF)[0]  # HTTP/1.1 200 OK
        self._parsed_response['status_line'] = status_line
        if DEBUG_FLAG: print "STATUS LINE: " + status_line + "\n"
        self._parsed_response['headers'] = self._data.split("\n\n")[0]
        self._parsed_response['csrf_token'], self._parsed_response['session_id'] = self.parse_response_cooikes("Set-Cookie")
        self._parsed_response['location'] = self.parse_new_location("Location")
        body_start_index = self._data.find("<html>")
        self._parsed_response['body'] = self._data[body_start_index:]

    def parse_response_cooikes(self, header):
        csrf_token = None
        session_id = None
        if header == 'Set-Cookie':
            if 'csrftoken' in self._parsed_response['headers']:
                index = self._parsed_response['headers'].find('csrftoken')
                csrf_token = self._parsed_response['headers'][index:].split(";")[0].split('=')[1]
            if 'sessionid' in self._parsed_response['headers']:
                index = self._parsed_response['headers'].find('sessionid')
                session_id = self._parsed_response['headers'][index:].split(";")[0].split('=')[1]
        else:
            raise ValueError("Incorrect cookie header!")

        return csrf_token, session_id


    def parse_new_location(self, header):
        new_location = None
        if header == 'Location':
            if 'Location' in self._parsed_response['headers']:
                index = self._parsed_response['headers'].find('Location')
                try:
                    new_location = self._parsed_response['headers'][index:].split(CRLF)[0].split(' ')[1].split('fakebook')[1] + "/"
                except:
                    return None
        else:
            raise ValueError("Incorrect Location header!")
        return new_location

    @staticmethod
    def initial_response_check(data):
        return not (data == "" or data == None)

    def get_session_id(self):
        return self._parsed_response['session_id']

    def get_csrf_token(self):
        return self._parsed_response['csrf_token']

    def get_new_location(self):
        return self._parsed_response['location']

    def get_status_line(self):
        return self._parsed_response['status_line']

    def get_body(self):
        return self._parsed_response['body']

    def is_valid(self):
        return self._isValid
