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

    BUFFER_SIZE = (2 ** 14) - 1 # 16 KB

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
    def connect(self, ip_address, port):
        """
        TODO: Implement connection to server sockets
        :param ip_address:
        :param port:
        :return: VOID
        """
        try:
            # make connection
            self.client_socket.connect((ip_address, int(port)))
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
    def receive(self, memory_allocation_size = None):
        """
        TODO: implement receives data from server socket
        :param memory_allocation_size:
        :return: deserialized data
        """
        memory_allocation_size = memory_allocation_size or self.BUFFER_SIZE
        server_response = self.client_socket.recv(memory_allocation_size)
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
        self.client_socket.close()
        # self.client_socket.shutdown()

