"""
Proxy thread file. Implements the proxy thread class and all its functionality. 
"""

from proxy_manager import ProxyManager
import pickle
# IMPORTANT READ BELOW NOTES. Otherwise, it may affect negatively your grade in this assignment
# Note about requests library
# use this library only to make request to the original server inside the appropiate class methods
# you need to create your own responses when sending them to the client (headers and body)
# request from client to the proxy are just based on url and private mode status. client also
# will send post requests if the proxy server requires authentification for some sites.
import requests

class ProxyThread(object):
    """
    The proxy thread class represents a threaded proxy instance to handle a specific request from a client socket
    """

    def __init__(self, conn, client_addr):
        self.proxy_manager = ProxyManager()
        self.client = conn
        self.client_id = client_addr[1]

    def get_settings(self):
        return self.proxy_manager

    def init_thread(self):
        """
        this is where you put your thread ready to receive data from the client like in assign #1
        calling the method self.client.rcv(..) in the appropiate loop
        and then proccess the request done by the client
        :return: VOID
        """
        return 0

    def client_id(self):
        """
        :return: the client id
        """
        return 0

    def _mask_ip_adress(self):
        """
        When private mode, mask ip address to browse in private
        This is easy if you think in terms of client-server sockets
        :return: VOID
        """
        return 0

    def process_client_request(self, data):
       """
       Main algorithm. Note that those are high level steps, and most of them may
       require futher implementation details
       1. get url and private mode status from client 
       2. if private mode, then mask ip address: mask_ip_address method
       3. check if the resource (site) is in cache. If so and not private mode, then:
           3.1 check if site is blocked for this employee 
           3.2 check if site require credentials for this employee
           3.3 if 3.1 or 3.2 then then client needs to send a post request to proxy
               with credentials to check 3.1 and 3.2 access 
               3.3.1 if credentials are valid, send a HEAD request to the original server
                     to check last_date_modified parameter. If the cache header for that 
                     site is outdated then move to step 4. Otherwise, send a response to the 
                     client with the requested site and the appropiate status code.
        4. If site is not in cache, or last_data_modified is outdated, then create a GET request 
           to the original server, and store in cache the reponse from the server. 
       :param data: 
       :return: VOID
       """
       return 0



    def _send(self, data):
        """
        Serialialize data 
        send with the send() method of self.client
        :param data: the response data
        :return: VOID
        """

    def _receive(self):
        """
        deserialize the data 
        :return: the deserialized data
        """
        return 0

    def head_request_to_server(self, url, param):
        """
        HEAD request does not return the HTML of the site
        :param url:
        :param param: parameters to be appended to the url
        :return: the headers of the response from the original server
        """
        return 0

    def get_request_to_server(self, url, param):
        """
        GET request
        :param url: 
        :param param: parameters to be appended to the url
        :return: the complete response including the body of the response
        """
        return 0


    def response_from_server(self, request):
        """
        Method already made for you. No need to modify
        :param request: a python dictionary with the following 
                        keys and values {'mode': 'GET OR HEAD', 'url': 'yoursite.com', 'param': []} 
        :return: 
        """
        mode = request['mode']
        url = request['url']
        param = request['param']
        if mode == "GET":
            return self.get_request_to_server(url, param)
        return self.head_request_to_server(url, param)

    def send_response_to_client(self, data):
        """
        The response sent to the client must contain at least the headers and body of the response 
        :param data: a response created by the proxy. Please check slides for response format
        :return: VOID
        """
        return 0

    def create_response_for_client(self):
        """
        
        :return: the response that will be passed as a parameter to the method send_response_to_client()
        """
        return 0

