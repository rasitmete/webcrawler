__author__ = "rasitmete"


import sys
import socket
import re
import select
import time
from simpleWebCrawler.packets.http_get import HttpGet
from simpleWebCrawler.packets.http_post import HttpPost
from simpleWebCrawler.packets.http_response import HttpResponse
from simpleWebCrawler.packets.http_status import HttpStatus
from simpleWebCrawler.communication.manager import CommunicationManager
from simpleWebCrawler.http_utility import RECV_BUFFER_SIZE
from simpleWebCrawler.http_utility import DEBUG_FLAG
from simpleWebCrawler.http_utility import Utility

class Runner():
    _csrf_token = ''
    _session_id = ''

    secrets = []
    visited_links = []
    queued_links = []
    current_page_url = "/"
    if DEBUG_FLAG: number_of_retry = 0

    def __init__(self, hostname, username, password):
        """ The constructer """
        self._hostname = hostname
        self._username = username
        self._password = password
        self._cm = CommunicationManager(hostname)


    def crawl(self):
        """ Within a loop this method will crawl all of the fakebook"""
        pckt = ''
        page_links = []
        if DEBUG_FLAG: print "/fakebook" + Runner.current_page_url

        received = self._cm.recv(RECV_BUFFER_SIZE)
        response = HttpResponse(received)
        if not response.is_valid(): # previous get message did not return a valid response... send again
            self._cm.connection_reset()
            if DEBUG_FLAG: Runner.number_of_retry += 1
            pckt = HttpGet(self._hostname, "/fakebook" + Runner.current_page_url, Runner._csrf_token, Runner._session_id).form_packet()
            self._cm.send(pckt)
            return True

        status = HttpStatus(response.get_status_line())
        if not status.is_valid():  #previous get message did not return a valid status... send again
            self._cm.connection_reset()
            pckt = HttpGet(self._hostname, "/fakebook" + Runner.current_page_url, Runner._csrf_token, Runner._session_id).form_packet()
            self._cm.send(pckt)
            return True

        ## If code reaches here, it means response is received and status is valid and can be parsed
        status_code = status.get_status_code()

        # check the status code... take action according to the status code
        if status_code == HttpStatus.Status_Codes['OK']: 
            """Crawler should continue crawling"""
            self._cm.reset_connection_reset_trial()
            body = response.get_body()
            page_links = re.findall('href=\"/fakebook[\'"]?([^\'" >]+)', body)

            # Current URL is processed, put in visited links
            if not Runner.current_page_url in Runner.visited_links:
                Runner.visited_links.append(Runner.current_page_url) 

            # put all the matching links into queued_links which is not in visited_links
            for link in page_links:
                if not link in Runner.visited_links and not link in Runner.queued_links:
                    Runner.queued_links.append(link)

            self.search_secret(body)

            # Everything went well, pop new URL
            if len(Runner.queued_links) > 0:
                Runner.current_page_url = Runner.queued_links.pop(0) 
            # Send freshly popped URL
            pckt = HttpGet(self._hostname, "/fakebook" + Runner.current_page_url, Runner._csrf_token, Runner._session_id).form_packet()
            self._cm.send(pckt)

        if status_code == HttpStatus.Status_Codes['MOVED_PERMANENTLY'] or status_code == HttpStatus.Status_Codes['FOUND']: ## 301, 302
            """ The page has been moved. parse the html, find new URL, and send the GET packet with the new URL"""
            new_location_url = response.get_new_location()
            if new_location_url:
                Runner.current_page_url = new_location_url
            pckt = HttpGet(self._hostname, "/fakebook" + Runner.current_page_url, Runner._csrf_token, Runner._session_id).form_packet()
            self._cm.send(pckt)

        if status_code == HttpStatus.Status_Codes['FORBIDDEN'] or status_code == HttpStatus.Status_Codes['NOT_FOUND']: ## 403, 404
            """This means the page is forbidden or not found, get a new URL from the queue"""
            if len(Runner.queued_links) > 0:
                Runner.current_page_url = Runner.queued_links.pop(0)
            pckt = HttpGet(self._hostname, "/fakebook" + Runner.current_page_url, Runner._csrf_token, Runner._session_id).form_packet()
            self._cm.send(pckt)

        if status_code == HttpStatus.Status_Codes['INTERNAL_SERVER_ERROR']:
            """ Send the packet again with a new socket since the old connection is closed now."""
            self._cm.connection_reset()
            pckt = HttpGet(self._hostname, "/fakebook" + Runner.current_page_url, Runner._csrf_token, Runner._session_id).form_packet()
            self._cm.send(pckt)
                
        if len(Runner.secrets) < 5:
            return True
        if len(Runner.queued_links) == 0:
            print "Crawled all pages! Could not find 5 secret!"
            return False
        return False

    def search_secret(self, body):
        secret_index = 0
        secret_index = body.find('secret_flag')
        # check if any secret has been found.. if so put into "secrets"
        if secret_index > 0:
            secret = re.findall('h2 class=\'secret_flag\' style="color:red">FLAG: ?([^\'"<]+)', body)
            Runner.secrets.append(secret[0])
        
    def run(self):
        """ This is where the loop logic take place """
        # Connect to the server
        self._cm.create_new_connection()
        packet = HttpGet(self._hostname, "/accounts/login/").form_packet()
        while True: ## Send the same request until successful status message with the cookies received
            self._cm.send(packet)
            received = self._cm.recv(RECV_BUFFER_SIZE, timeout=0.5)
            response = HttpResponse(received)     

            if response.is_valid():
                status = HttpStatus(response.get_status_line())
                if status.is_valid():
                    status_code = status.get_status_code()
                    if status_code == HttpStatus.Status_Codes['OK']:
                        break    
   
        Runner._csrf_token = response.get_csrf_token()
        Runner._session_id = response.get_session_id()

        # post credentials: using the credentials and the cookeis, form the post packet 
        credentials = dict(username=self._username, password=self._password, csrfmiddlewaretoken=Runner._csrf_token)
        packet =  HttpPost(self._hostname, "/accounts/login/", Runner._csrf_token, Runner._session_id, credentials).form_packet()

        while True: ## Send the same post reques until successful status message with the cookies received, update the session id with the last post resp.
            self._cm.send(packet)
            received = self._cm.recv(RECV_BUFFER_SIZE, timeout=0.5)  
            response = HttpResponse(received)                

            if response.is_valid():
                status = HttpStatus(response.get_status_line())
                if status.is_valid():
                    status_code = status.get_status_code()
                    if status_code == HttpStatus.Status_Codes['OK'] or status_code == HttpStatus.Status_Codes['FOUND']:
                        Runner._session_id = response.get_session_id()
                        break            

        # send GET /fakebook/, then begin crawling
        packet = HttpGet(self._hostname, "/fakebook/", Runner._csrf_token, Runner._session_id).form_packet()
        self._cm.send(packet)
       
        try:
            while self.crawl():
                pass
        finally:
            if DEBUG_FLAG:
                print "REMAINING QUEUED LIST LENGHT: " + str(len(Runner.queued_links))
                print "VISITED QUEUE LENGHT: " + str(len(Runner.visited_links))
                print "UNSUCCESSFUL ATTEMPTS: " + str(Runner.number_of_retry)
                print ""

            for secret in Runner.secrets:
                print secret

            self._cm.close_connection()
        