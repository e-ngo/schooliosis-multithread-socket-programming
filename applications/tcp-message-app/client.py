"""
This module implements the Client class
"""
from helpers import (
    getIpFromUser,
    getPortFromUser,
    MAX_NUM_CONNECTIONS,
    BUFFER_SIZE,
    ServerDisconnect,
)
import socket
import pickle
import datetime


class Client:
    """Client class is in charge of connecting, sending, and retrieving from a socket

    """
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
        """Closes the current connection

        """
        self.tcp_socket.close()
        
    def send(self, data):
        """send requests to the server

        """
        data_serialized = pickle.dumps(data)
        self.tcp_socket.send(data_serialized)

    def retrieve(self):
        """retrieve responses from the server

        """
        server_response = self.tcp_socket.recv(BUFFER_SIZE)
        if not server_response:
            raise ServerDisconnect()
        # Deserializes the data.
        server_data = pickle.loads(server_response)
        return server_data

if __name__ == '__main__':
    # handles cyclic imports
    from TCPClientHandler import TCPClientHandler
    client = Client()
    client_wrapper = TCPClientHandler(client)
    client_wrapper.run()