import socket
import pickle

class ServerDisconnect(Exception):
    """Signals server disconnect

    """
    pass

def network_exception_handler(func):
    def wrap_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except socket.error as sock_error:
            print(f"An HTTPError occurred: {sock_error}")
        except Exception as e:
            print(f"Something went wrong: {e}")
    return wrap_func

class Client:
    """
    This class represents your client class that will send requests to the proxy server and will hand the responses to 
    the user to be rendered by the browser, 
    """
    BUFFER_SIZE = 4096
    # ProxyServer constants
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 12000

    def __init__(self):
        self.init_socket()

    def init_socket(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Socket successfully created")
        except socket.error as err:
            print("socket creation failed with error", (err))

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
        path, host = self.parse_url(data['url'])
        # TODO: Make HTTP method dynamic?
        # for post requests...
        # Content-Type: {content_type}\r
        # Content-Length: {content_length}\r
        header = f"""\
        GET {path} HTTP/1.1\r
        Host: {host}\r
        Connection: close\r
        \r\n"""

        data["request_message"] = header
        # connect to ProxyServer
        self._connect_to_server(self.SERVER_HOST, self.SERVER_PORT)
        # send info to ProxyServer
        self._send(data)


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
        # handle response(extract headers, return pretty params)

        # close connection after request?
        self.client_socket.close()
        # render HTML


        return response

if __name__=="__main__":
    client = Client()
    client._connect_to_server(Client.SERVER_HOST,Client.SERVER_PORT)