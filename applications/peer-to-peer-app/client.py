# -*- coding: utf-8 -*-
""" The client
This file has the class client that implements a client socket.
Note that you can replace this client file by your client from
assignment #1.
"""
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
        except ServerDisconnect:
            print("Server has disconnected")
        except Exception as e:
            print(f"Something went wrong: {e}")
    return wrap_func

class Client:

    BUFFER_SIZE = 65536
    # ProxyServer constants
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 12001

    def __init__(self):
        """
        TODO: implement this contructor
        Class contructor
        """
        self.init_socket()

    def init_socket(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as err:
            print("socket creation failed with error", (err))

    @network_exception_handler
    def connect(self, ip_adress, port):
        """
        TODO: Implement connection to server sockets
        :param ip_adress:
        :param port:
        :return: VOID
        """
        try:
            # Connects to the server using its host IP and port
            self.client_socket.connect((host_ip, port))
        except OSError:
            # socket already connected
            pass

    @network_exception_handler
    def send(self, data):
        """
        TODO: Implement client socket send method
        :param data: raw_data. This data needs to be
                     serialized inside this method
                     with pickle before being sent.
                     You can also serialize objects
                     with pickle
        :return: VOID
        """
        data_serialized = pickle.dumps(data)
        self.client_socket.send(data_serialized)

    @network_exception_handler
    def recieve(self, memory_allocation_size):
        """
        TODO: implement receives data from server socket
        :param memory_allocation_size:
        :return: deserialized data
        """
        server_response = self.client_socket.recv(self.BUFFER_SIZE)
        if not server_response:
            raise ServerDisconnect()
        # Deserializes the data.
        server_data = pickle.loads(server_response)
        return server_data

    def close(self):
        """
        TODO: implement the close mechanish of a client socket
        :return: VOID
        """
        pass
