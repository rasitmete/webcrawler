__author__ = "rasitmete"

from simpleWebCrawler.http_utility import HTTP_VERSION


class HttpStatus():
    """ Status Codes will be fetched here, and validity of the status messages are gonna be checked here
    """
    Status_Codes = dict(OK = 200,
                    MOVED_PERMANENTLY = 301,
                    FOUND = 302,
                    FORBIDDEN = 403,
                    NOT_FOUND = 404,
                    INTERNAL_SERVER_ERROR = 500)


    def __init__(self, status_line):
        # in this case the same packet should be sent
        self._isValid = True
        if not HttpStatus.initial_status_check(status_line):
            self._isValid = False
       
        self._http_version = status_line.split(" ")[0]
        if not self._http_version == HTTP_VERSION:
            self._isValid = False 
        try:
            self._status_code  = int(status_line.split(" ")[1])
        except:
            self._isValid = False

    @staticmethod
    def initial_status_check(status_line):
        return not (status_line == None or status_line == "")

    def get_status_code(self):
        return self._status_code

    def is_valid(self):
        return self._isValid