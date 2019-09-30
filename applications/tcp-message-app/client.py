"""

a.) TCP Client in charge of
1.) Connect to server
2.) Send requests to the server
3.) Retrieve responses from the server.
Retrieved responses from the server are handeld by TCPClientHandler, 
    which is the worker class that provides all the menu actions executed from client size.
b.) after executing client.py script, should show a menu where user can select different actions.
c.) Options

Design:

Class client:


"""
from helpers import (
    getIpFromUser,
    getPortFromUser,
    MAX_NUM_CONNECTIONS,
    BUFFER_SIZE,
    ServerDisconnect,
    TEST_PORT
)
import socket
import pickle
import datetime


class Client:

    def __init__(self, ip=None, port=None, name=None):
        if not ip:
            # Prompt user for IP
            ip = getIpFromUser("Enter the server IP Address: ")
        if not port:
            # Prompt user for port
            port = getPortFromUser("Enter the server port:")
        self.ip = ip
        self.port = port
        self.client_name = name if name else input("Your id key (i.e your name): ")
        self.client_id = None
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """Connects to the server
        
        """
        # Connects to the server using its host IP and port
        self.tcp_socket.connect((self.ip, self.port))
        
    def disconnect(self):
        self.tcp_socket.close()
        
    def send(self, data):
        """send requests to the server

        """
        try:
            data_serialized = pickle.dumps(data)
            self.tcp_socket.send(data_serialized)
        except socket.error as socket_exception:
            print("Issue sending data")

    def retrieve(self):
        """retrieve responses from the server

        """
         # Server response is received. However, we need to take care of data size
        server_response = self.tcp_socket.recv(BUFFER_SIZE)
        if not server_response:
            raise ServerDisconnect()
        # Desearializes the data.
        server_data = pickle.loads(server_response)
        return server_data

if __name__ == '__main__':
    from TCPClientHandler import TCPClientHandler

    client = Client('127.0.0.1', TEST_PORT)
    client_wrapper = TCPClientHandler(client)
    client_wrapper.run()