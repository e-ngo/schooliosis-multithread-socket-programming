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
import socket
import time
# import validators

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

def parse_for_field(response, field = ""):
    """
    Given an HTTP Response, parses for certain attribute...
    """
    lines = response.split("\r\n")
    map = {}

    map["body"] = lines[-1]
    # get HTML
    # if field == "body":
    #     # if looking for HTML content or POST body parameters...
    #     return map["body"]

    map["top"] = lines[0]
    # get HTTP Method path, and version...
    # if field == "top":
    #     # ie. GET / HTTP/1.1
    #     return map["top"]

    map["method"] = lines[0].split(' ')[0]
    # if field == "method":
    #     # ie. GET
    #     return map["method"]

    map["url"] = lines[0].split(' ')[1]
    # if field == "url":
    #     # ie. /
    #     return map["url"]

    map["http_version"] = lines[0].split(' ')[2][5:]
    # if field == "http_version":
    #     # ie. 1.1
    #     return map["http_version"]

    for i in range(1, len(lines) - 1):
        try:
            # for each line not header and body
            k, v = lines[i].split(": ")
            map[k] = v
        except ValueError:
            pass
    if field == "":
        return map
    try:
        return map[field]
    except KeyError:
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
    KEEP_ALIVE_REQUESTS=5 # max number of requests made over connection

    def __init__(self, conn, client_addr, server_ip):
        self.proxy_manager = ProxyManager()
        self.client = conn
        self.client_id = client_addr[1]
        self.client_ip = ""
        self.permission = False # whether or not user is authenticated
        self.role = "EMPLOYEE" # role of user "CEO, CTO, etc.." Default is EMPLOYEE
        self.KEEP_ALIVE_TIME=115 # time to keep idle connection alive(seconds)
        self.server_ip = server_ip

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

    # def is_valid_url(self, http_request_string):
    #     """
    #     Determines whether or not given http_request_string has
    #     a valid url
    #     """
    #     url = parse_for_field(http_request_string, "url")
    #     return True if validators.url(url) else False

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
        except socket.timeout:
            print("Client {} has timed out.".format(self.client_id))
        except socket.error as sock_error:
            print(f"An HTTPError occurred: {sock_error}")
        except ClientDisconnect:
            print("Client has disconnected")
        # except Exception as e:
        #     print(f"Something went wrong: {e}")
            # send to client error?
        # clean up stuff...
        self.client.close()

    def client_id(self):
        """
        :return: the client id
        """
        return self.client_id

    def _mask_ip_address(self):
        """
        When private mode, mask ip address to browse in private
        This is easy if you think in terms of client-server sockets
        :return: VOID
        """
        self.client_ip = self.server_ip
    
    def respond_ok(self, params):
        """
        Sends 200 response to client
        """
        req_map = params['request_map']
        response = params['response']
        http_version = req_map["http_version"]
        content_length = len(response.text)

        # print(response.text)

        self._send("HTTP/{} 200 OK\r\nDate: Tue, 22 Oct 2019 06:40:46 GMT\r\nServer: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/5.4.16 mod_perl/2.0.10 Perl/v5.16.3\r\nX-Powered-By: PHP/5.4.16\r\nContent-Length: {}\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n{}".format(http_version, content_length, response.text))

    def respond_not_modified(self, params):
        """
        Sends 304 response to client
        """
        # req_map = params['request_map']
        # response = params['response']
        # http_version = req_map["http_version"]
        # content_length = len(response.content)

        # self._send("HTTP/{} 200 OK\r\nDate: Tue, 22 Oct 2019 06:40:46 GMT\r\nServer: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/5.4.16 mod_perl/2.0.10 Perl/v5.16.3\r\nX-Powered-By: PHP/5.4.16\r\nContent-Length: {}\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n{}".format(http_version, content_length, response.content))

    def respond_unauthorized(self, params):
        """
        Sends 401 response to client
        """
        # response should include Proxy-Authenticate: Basic realm="proxyserver"
#         HTTP/1.1 401 Unauthorized 
# Date: Wed, 21 Oct 2015 07:28:00 GMT
# WWW-Authenticate: Basic realm="Access to staging site"

    def respond_bad_request(self, params):
        """
        Sends 400 response to client
        """
        pass
    def respond_not_found(self, params):
        """
        Sends 404 response to client
        """
        pass
    def respond_need_auth(self, params):
        """
        Sends 407 response to client
        """
        pass
    def respond_forbidden(self, params):
        """
        Sends 403 response to client
        """
        pass

    def handle_client_response(self, code, params):
        """
        Handles which response to send to users given code.
        """
        if code == 200:
            self.respond_ok(params)
        elif code == 304:
            self.respond_not_modified(params)
        elif code == 401:
            self.respond_unauthorized(params)
        elif code == 400:
            self.respond_bad_request(params)
        elif code == 404:
            self.respond_not_found(params)
        elif code == 407:
            self.respond_need_auth(params)
        elif code == 403:
            self.respond_forbidden(params)
        else:
            raise Exception("Code not understood")
    
    def check_permissions(self, resource):
        """
        Because after login, user role is known, check proxy manager to see if userrole
        is allowed access to resource.
        :return: Bool if user is able to access resource.
        """
        if resource != "god":
            return True
        return False

    def login(self, username, password, mask=False):
        """
        Gets userrole from proxy manager, returns True if user is authorized
        """
        if mask:
            self._mask_ip_address()
        # check proxymanager if user/pw is in db.
        if username == "Bob" and password == "123":
            # self.proxy_manager
            self.role = "CEO"
            return True
        return False

    def handle_auth(self, request_map, response_params):
        """
        Note that execution flows if the user is authenticating/authenticated
        :param request_map: used to check request
        :param response_params: used in response
        """
        if not self.permissions:
            # ask for permissions
            if request_map["method"] != "POST":
                # if not an attempt to login and not logged in, ask to login
                self.handle_client_response(407, response_params)
                return ;

            body = request_map["params"]
            post_params = params_to_map(body)
            if "user_name" not in post_params or "password" not in post_params:
                # 403 error: Something is wrong with input params...
                self.handle_client_response(403, response_params)
                return ;

            username = post_params["user_name"]
            password = post_params["password"]
            self.permission = self.login(username, password, mask=True)

            if not self.permission:
                # insufficient permissions
                self.handle_client_response(401, response_params)
                return ;

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
        try:
            request_map = parse_for_field(http_request_string)
            # make sure correct parameters?
            http_version = request_map["http_version"]
            method = request_map["method"]
            if http_version != "1.0" or http_version != "1.1":
                # complain
                pass

            url = request_map["url"]
            url, query_params = extract_query_params(url, "is_private_mode")

            query_params = params_to_map(query_params)
            # holds data needed to parse in respond
            response_params = { 'request_map': request_map  }
            # get client's ip
            self.client_ip = request_map["Host"]

            if int(query_params["is_private_mode"]) == 1:
                # make sure authed
                self.handle_auth(request_map, response_params)
                # user has sufficient permissions at this point.            
                response = self.get_request_to_server(url, request_map)
            else:
                # check if cached...
                # if is_cached(url):
                # make head request
                # else:
                if needs_auth(url):
                    self.handle_auth(request_map, response_params)
                # in handle_cache checks if proxy manager has url. if it does, it does a head request,
                # checks if_modified_since date, if it is ok, it sends 300 instead. else execution flows
                # back here.
                self.handle_cache(request_map, response_params)

                response = self.get_request_to_server(url, request_map)

            if 200<=response.status_code< 300 or response.status_code == 304:
                if int(query_params["is_private_mode"]) != 1:
                    # self.
                    pass
                # check exists
                response_params['response'] = response
                
                self.handle_client_response(200, response_params)
            else:
                self.handle_client_response(404, response_params)
            # print(http_request_string)
            # Check response... 
            # sample response
            # self._send("""HTTP/1.1 200 OK\r\nDate: Tue, 22 Oct 2019 06:40:46 GMT\r\nServer: Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/5.4.16 mod_perl/2.0.10 Perl/v5.16.3\r\nX-Powered-By: PHP/5.4.16\r\nContent-Length: 7097\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n<html><head><title>Blah</title></head><body style="color:red;">Boo</body></html>""")
        except ParsingError:
            # this is encountered when during parsing of the headers, there is an error.
            # In this case, a 400 Bad Request is sent back to client.
            self.handle_client_response(400, {})
           
    def _send(self, data):
        """
        Serialialize data 
        send with the send() method of self.client
        :param data: the response data
        :return: VOID
        """
        data_serialized = pickle.dumps(data)
        self.client.send(data_serialized)

    def _receive(self):
        """
        deserialize the data 
        :return: the deserialized data
        """
        self.client.settimeout(self.KEEP_ALIVE_TIME)
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
        :param param: additions to session header
        :return: the headers of the response from the original server
        """
        # with requests.Session() as session:
        #     response = session.head(url)
    
        headers = {}
        # add custom headers
        if "Connection" in param:
            headers["Connection"] = param["Connection"]
        if "Keep-Alive" in param:
            headers["Keep-Alive"] = param["Keep-Alive"]
        response = requests.head(url, headers = headers)
        print("HEAD to", url)
        print(res)
        return res
        

    def get_request_to_server(self, url, param):
        """
        GET request
        :param url: 
        :param param: additions to session header
        :return: the complete response including the body of the response
        """
        # with requests.Session() as session:
            # session.headers.update({})
            # response = session.get(url)
        headers = {}
        # add custom headers
        if "Connection" in param:
            headers["Connection"] = param["Connection"]
        if "Keep-Alive" in param:
            headers["Keep-Alive"] = param["Keep-Alive"]
        response = requests.get(url, headers = headers)
        print("GET to", url)
        print(response)
        return response


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