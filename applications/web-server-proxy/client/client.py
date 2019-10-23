import socket
import pickle

class ServerDisconnect(Exception):
    """Signals server disconnect

    """
    pass

class ParsingError(Exception):
    """
    Signals error when parsing
    """
    pass

def network_exception_handler(func):
    def wrap_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except socket.error as sock_error:
            print(f"An HTTPError occurred: {sock_error}")
        except ServerDisconnect:
            print("Server has disconnected")
        # except Exception as e:
            # print(f"Something went wrong: {e}")
    return wrap_func


def parse_for_field(response, field):
    """
    Given an HTTP Response, parses for certain field...
    """
    lines = response.split("\r\n")
    
    for line in lines:
        # if field == "\r\n":
            # if looking for HTML content...

        if line.startswith(field):
            return line
        
    
    raise ParsingError(f"Error parsing for field: {field}")

class Client:
    """
    This class represents your client class that will send requests to the proxy server and will hand the responses to 
    the user to be rendered by the browser, 
    """
    BUFFER_SIZE = 4096
    # ProxyServer constants
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 12001

    def __init__(self):
        self.init_socket()

    def init_socket(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Socket successfully created")
        except socket.error as err:
            print("socket creation failed with error", (err))

    def _disconnect(self):
        self.client_socket.close()

    @network_exception_handler
    def _connect_to_server(self, host_ip, port):
        """
        Connects to server 
        remember to handle exceptions
        :param host_ip: 
        :param port: 
        :return: VOID
        """
        # Connects to the server using its host IP and port
        self.client_socket.connect((host_ip, port))

    @network_exception_handler
    def _send(self, data):
        """
        1. Serialize data
        2. implements the primitive send() call from the socket
        :param data: {url: url, private_mode: True or False, header: header_generated_by_client_to_original_server}
        :return: VOID
        """
        data_serialized = pickle.dumps(data)
        self.client_socket.send(data_serialized)

    @network_exception_handler
    def _receive(self):
        """
        1. Implements the primitive rcv() method from socket
        2. Desirialize data after it is recieved
        :return: the desirialized data 
        """
        server_response = self.client_socket.recv(self.BUFFER_SIZE)
        if not server_response:
            raise ServerDisconnect()
        # Deserializes the data.
        server_data = pickle.loads(server_response)
        return server_data

    def parse_url(self, url):
        """Parses url for path and host

        """
        # host: (www.)subdomain.domain.com
        # path: /(path...)
        
        # remove protocol part...
        start_of_host = url.find("://")
        if start_of_host > -1:
            start_of_host += 3
        else:
            start_of_host = 0
        start_of_path = url.find("/", start_of_host)
        path = ''
        if start_of_path == -1:
            # if path part not found,
            host = url[start_of_host:]
        else:
            host = url[start_of_host:start_of_path]
            path = url[start_of_path:]
        return (path, host)

    @network_exception_handler
    def request_to_proxy(self, data):
        """
        Create the request from data 
        request must have headers and can be GET or POST. depending on the option
        then send all the data with _send() method
        :param data: url and private mode 
        :return: VOID
        """
        """
        Example from SO: https://stackoverflow.com/questions/34192093/python-socket-get
        """
        # path, host = self.parse_url(data['url'])
        original_url = data['url'] + f"?is_private_mode={data['is_private_mode']}"
        
        body = ""
        try:
            if data['user_name']:
                body += f"user_name=${data['user_name']}"
        except KeyError:
            # user_name not provided...
            pass
        try:
            if data['password']:
                if body:
                    body += "&"
                body += f"password=${data['password']}"

        except KeyError:
            pass

        if len(body):
            # if there is body...
            content_length = len(body)
            http_request = f"""POST {original_url} HTTP/1.1\r\nHost: {data['client_ip']}\r\nAccept: text/html,application/xhtml+xml\r\nAccept-Language: en-us,en;q=0.5\r\nAccept-Encoding: gzip,deflate\r\nAccept-Charset: ISO-8859-1,utf-8;q=0.7\r\nKeep-Alive: 0\r\nConnection: close\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {content_length}\r\n\r\n{body}"""
        else:
            http_request = f"""GET {original_url} HTTP/1.1\r\nHost: {data['client_ip']}\r\nAccept: text/html,application/xhtml+xml\r\nAccept-Language: en-us,en;q=0.5\r\nAccept-Encoding: gzip,deflate\r\nAccept-Charset: ISO-8859-1,utf-8;q=0.7\r\nKeep-Alive: 0\r\nConnection: close\r\n\r\n"""
        # connect to ProxyServer
        self._connect_to_server(self.SERVER_HOST, self.SERVER_PORT)
        # send info to ProxyServer
        self._send(http_request)


    @network_exception_handler
    def response_from_proxy(self):
        """
        the response from the proxy after putting the _recieve method to listen.
        handle the response, and then render HTML in browser. 
        This method must be called from web_proxy_server.py which is the home page of the app
        :return: the response from the proxy server
        """
        # receive data
        response = self._receive()
        # handle response(extract headers, return pretty params?...)
        print("Resonse form proxy", response)
        # non-persistent: closer socket afterwards...
        self._disconnect()
        # render HTML
        return response

if __name__=="__main__":
    # test script
    client = Client()
    client.request_to_proxy({'url': 'https://google.com/', 'is_private_mode': False, 'client_ip': '127.0.0.1'})
    res = client.response_from_proxy()
    print(res)