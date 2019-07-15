__author__ = "rasitmete"


import socket
import sys
import time
from simpleWebCrawler.http_utility import DEBUG_FLAG

class CommunicationManager():
    """ This class is responsible for socket operation and timeout adjustment """

    def __init__(self, hostname):
        self._hostname = hostname
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._http_port = 80 ## default HTTP port
        self._timeout = 0.05
        self._connection_reset_trial = 0
        self._consecutive_successful_requests = 0

    def connection_reset(self):
        """ In case of a connection close by the server or invalid response, this resets the connection"""
        self._connection_reset_trial += 1
        self._consecutive_successful_requests = 0 
        self.close_connection()
        self.create_new_connection()

    def create_new_connection(self):
        """ Wait until the connection is established. Works even the network goes down while crawling.. """
        while True:
            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(5)        
                self._socket.connect((self._hostname, self._http_port))
                return False
            except socket.error:
                self.close_connection()
    
    def close_connection(self):
        self._socket.close()
    
    def adjust_timeout(self):
        """ If there are 3 or more unsuccesful attemp of receiving data from the recv buffer, increase the timeout by 0.01
            otherwise there will be many unsuccesful attemp which will block the buffer.s"""      
        if self._connection_reset_trial >= 3:
            self._timeout += 0.01

    def reset_connection_reset_trial(self):
        """ I the request returned with status 200, then this will try to reduce the timeout to crawl faster"""
        self._connection_reset_trial = 0
        self._consecutive_successful_requests += 1
        if self._consecutive_successful_requests > 3: # Current timeout can be decreased 
            self._timeout -= 0.01
        if self._timeout < 0.01: # least possible timeout 
            self._timeout = 0.01

    def send(self, packet):
        self._socket.sendall(packet)

    def recv(self, size, timeout=0.02):
        """ this recv waits for the receival of all the data to prevent getting uncomplete buffer"""
        if timeout != 0.02:
            self._timeout = timeout
        self.adjust_timeout() # according to the network behaviour, the recv timout will be adjusted
        if DEBUG_FLAG: print "RECV buffer timeout: " + str(self._timeout)
        self._socket.setblocking(0)
        start = time.time()
        data = []
        while True:  
            # if server send some data but stopped connection after statu 500 or didnt get data for timeout time  
            if data and (time.time() - start) > self._timeout:
                break
            # if no data received within time interval or the timeout is bigger than 2*_timeout second..
            elif time.time() - start > 2*self._timeout: 
                break
            try:
                received = self._socket.recv(size)
                if received:
                    data.append(received)
                    start = time.time() 
            except:
                pass
        return ''.join(data)

