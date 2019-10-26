"""
Proxy thread file. Implements the proxy thread class and all its functionality. 
"""

from .proxy_manager import ProxyManager
import pickle
# IMPORTANT READ BELOW NOTES. Otherwise, it may affect negatively your grade in this assignment
# Note about requests library
# use this library only to make request to the original server inside the appropiate class methods
# you need to create your own responses when sending them to the client (headers and body)
# request from client to the proxy are just based on url and private mode status. client also
# will send post requests if the proxy server requires authentification for some sites.
import requests
import socket
import time
import validators

class ClientDisconnect(Exception):
    """Signals client disconnect

    """
    pass

class ParsingError(Exception):
    """
    Signals error when parsing
    """
    pass

class InvalidHTTPRequest(Exception):
    """
    Signals whether HTTP Request is invalid
    """
    pass

def extract_query_params(url, explicit_field=""):
    """
    Splits url into its path and its query parameters
    ie. google.com/blah?v=3 => (google.com/blah, ?v=3)
    :return: (url, query_params)
    """
    # if explicit_field:
    last_instance = url.rfind("?")
    if last_instance < 0:
        return (url, "")
    substr = url[last_instance+1:]
    if explicit_field:
        # if requires parameter to start with certain field...
        if not substr.startswith(explicit_field):
            return (url, "")
    return (url[:last_instance], substr)

def params_to_map(data):
    """
    Parses a query parameter or POST body parameter into map
    """
    # needs to be at least s=1
    if len(data) < 3:
        return {}
    # remove ?
    data = data[1:] if data[0] == "?" else data
    fields = data.split('&')
    mapping = {}
    for field in fields:
        try:
            k, v = field.split('=')
        except ValueError:
            # if error parsing split
            return {}
        mapping[k] = v
    return mapping

def parse_for_field(response, field):
    """
    Given an HTTP Response, parses for certain attribute...
    """
    lines = response.split("\r\n")
    # get HTML
    if field == "\r\n" or field == "body":
        # if looking for HTML content or POST body parameters...
        return lines[-1]
    # get HTTP Method path, and version...
    if field == "top":
        # ie. GET / HTTP/1.1
        return lines[0]
    if field == "method":
        # ie. GET
        return lines[0].split(' ')[0]
    if field == "url":
        # ie. /
        return lines[0].split(' ')[1]
    if field == "http_version":
        # ie. 1.1
        return lines[0].split(' ')[2][5:]
        
    for line in lines:
        try:
            index = line.index(field)
            return line[index + len(field) + 2:]
        except ValueError:
            pass
    
    raise ParsingError(f"Error parsing for field: {field}")

def network_exception_handler(func):
    def wrap_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except socket.error as sock_error:
            print(f"An HTTPError occurred: {sock_error}")
        except ClientDisconnect:
            print("Client has disconnected")
        except Exception as e:
            print(f"Something went wrong: {e}")
        # raise ClientDisconnect()
    return wrap_func

class ProxyThread:
    """
    The proxy thread class represents a threaded proxy instance to handle a specific request from a client socket
    """
    BUFFER_SIZE=4096
    KEEP_ALIVE_TIME=115 # time to keep idle connection alive(seconds)
    KEEP_ALIVE_REQUESTS=5 # max number of requests made over connection

    def __init__(self, conn, client_addr):
        self.proxy_manager = ProxyManager()
        self.client = conn
        self.client_id = client_addr[1]

    def get_settings(self):
        return self.proxy_manager

    def is_non_persistent(self, http_request_string):
        """
        Determines whether or not given http_request_string has
        persistent features (Connection: Open, etc., 1.0, etc..)
        """
        if parse_for_field(http_request_string, "http_version") != "1.1":
            return True
        if parse_for_field(http_request_string, "Connection") == "Keep-Alive":
            # set keep alive time.
            try:
                self.KEEP_ALIVE_TIME = min(int(parse_for_field(http_request_string, "Keep-Alive")), self.KEEP_ALIVE_TIME)
            except ParsingError:
                # Keep-Alive field does not exist. Use default timeout
                pass
            return False
        return True

    def is_valid_url(self, http_request_string):
        """
        Determines whether or not given http_request_string has
        a valid url
        """
        url = parse_for_field(http_request_string, "url")
        return True if validators.url(url) else False

    def init_thread(self):
        """
        this is where you put your thread ready to receive data from the client like in assign #1
        calling the method self.client.rcv(..) in the appropiate loop
        and then proccess the request done by the client
        :return: VOID
        """
        try:
            # grab first request
            client_req = self._receive()
            non_persistent = self.is_non_persistent(client_req)
            num_of_requests = 0

            while True:
                # start timer
                tick = time.time()
                self.process_client_request(client_req)
                # increment number of request/responses
                num_of_requests += 1
                # if non_persistent or idle time is up or number of requests exceeded.
                if non_persistent or time.time() - tick > self.KEEP_ALIVE_TIME or num_of_requests >= self.KEEP_ALIVE_REQUESTS:
                    break
                client_req = self._receive()
        except Exception as e:
            print("Something has gone wrong w/in loop:", e)
            # send to client error?
        # clean up stuff...
        self.client.close()

    def client_id(self):
        """
        :return: the client id
        """
        return self.client_id

    def _mask_ip_adress(self):
        """
        When private mode, mask ip address to browse in private
        This is easy if you think in terms of client-server sockets
        :return: VOID
        # ask about ...
        https://realpython.com/python-requests/
        """
        return 0

    def process_client_request(self, http_request_string):
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
        :param http_request_string: 
        :return: VOID
        """
        # make sure correct parameters?
        http_version = parse_for_field(http_request_string, "http_version")
        if http_version != "1.0" or http_version != "1.1":
            # complain
            pass
        url = parse_for_field(http_request_string, "url")
        url, query_params = extract_query_params(url, "is_private_mode")

        query_params = params_to_map(query_params)

        if int(query_params["is_private_mode"]) == 1:
            # if private mode, mask ip. how to?
            pass


            
        print(http_request_string)
        # sample response
        self._send("""HTTP/1.1 200 OK\r\nDate: Tue, 22 Oct 2019 06:40:46 GMT\r\nServer: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/5.4.16 mod_perl/2.0.10 Perl/v5.16.3\r\nX-Powered-By: PHP/5.4.16\r\nContent-Length: 7097\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n<html><head><title>Blah</title></head><body>Boo</body></html>""")
           
    @network_exception_handler
    def _send(self, data):
        """
        Serialialize data 
        send with the send() method of self.client
        :param data: the response data
        :return: VOID
        """
        data_serialized = pickle.dumps(data)
        self.client.send(data_serialized)

    @network_exception_handler
    def _receive(self):
        """
        deserialize the data 
        :return: the deserialized data
        """
        client_request = self.client.recv(self.BUFFER_SIZE)
        if not client_request:
            raise ClientDisconnect()
        # Deserializes the data.
        client_data = pickle.loads(client_request)
        return client_data

    def head_request_to_server(self, url, param):
        """
        HEAD request does not return the HTML of the site
        :param url:
        :param param: parameters to be appended to the url as a mapping.
        :return: the headers of the response from the original server
        """
        res = requests.head(url, params=param)
        print("HEAD to", url)
        print(res)
        return res
        

    def get_request_to_server(self, url, param):
        """
        GET request
        :param url: 
        :param param: parameters to be appended to the url
        :return: the complete response including the body of the response
        """
        res = requests.get(url, params=param)
        print("GET to", url)
        print(res)
        return res


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
        """HTTP/1.1 200 OK\r\nDate: Tue, 22 Oct 2019 06:40:46 GMT\r\nServer: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/5.4.16 mod_perl/2.0.10 Perl/v5.16.3\r\nX-Powered-By: PHP/5.4.16\r\nContent-Length: 7097\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n<html><head><title>Blah</title></head><body>Boo</body></html>"""

    def create_response_for_client(self):
        """
        
        :return: the response that will be passed as a parameter to the method send_response_to_client()
        """
        """HTTP/1.1 200 OK\r\nDate: Tue, 22 Oct 2019 06:40:46 GMT\r\nServer: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/5.4.16 mod_perl/2.0.10 Perl/v5.16.3\r\nX-Powered-By: PHP/5.4.16\r\nContent-Length: 7097\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n<html><head><title>Blah</title></head><body>Boo</body></html>"""

if __name__=="__main__":
    d, k = extract_query_params("gogole.com/dsf?s=5", "s")
    print(params_to_map(k))