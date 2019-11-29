# -*- coding: utf-8 -*-
""" The server
This file has the class client that implements a server socket.
Note that you can replace this server file by your server from
assignment #1.
"""
import socket
import pickle
import threading
import os

class ClientDisconnect(Exception):
    """Signals client disconnect

    """
    pass

class Server(object):

    BACKLOG = 50
    MAX_DATA_RECV = (2 ** 14) - 1

    def __init__(self, host_ip = None, host_port = None):
        """
        TODO: implement this constructor
        Class contructor
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.host_ip = host_ip
        self.host_port = host_port

    def listen(self, func = None):
        """
        TODO: implement this method
        Listen for new connections
        :return: VOID
        """
        try:
            # associate the socket to host and port
            self.server_socket.bind((self.host_ip, self.host_port))
            # listen and accept clients
            self.server_socket.listen()
            print(f"Server started\nListening at {self.host_ip}({self.host_port}):")
            while True:
                self.accept(func)
            
        except socket.error as sock_error:
            print(sock_error)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print("An exception has occurred", e)

        self.server_socket.close()
        print("Closing the server")
        os._exit(0)

    def accept(self, func = None):
        """
        TODO: implement this method
        Accept new clients
        :return:
        """
        client_sock, addr = self.server_socket.accept()
        self.clients[addr[1]] = client_sock
        print(f"Client {addr} has connected!")
        thread = threading.Thread(target=self.threaded_client, args=(client_sock, addr, func))
        thread.start()

    def receive(self, client_sock, memory_allocation_size = None):
        """
        TODO: implement this method
        Receives data from clients socket
        :param memory_allocation_size:
        :return: deserialized data
        """
        memory_allocation_size = memory_allocation_size or self.MAX_DATA_RECV
        # client_sock.settimeout(self.KEEP_ALIVE_TIME)
        client_request = client_sock.recv(self.MAX_DATA_RECV)
        if not client_request:
            raise ClientDisconnect()
        # Deserializes the data.
        client_data = pickle.loads(client_request)
        return client_data

    def send(self, client_sock, data):
        """
        TODO: implement this method
        Implements send socket send method
        :param data: raw_data. This data needs to be
                     serialized inside this method
                     with pickle before being sent.
                     You can also serialize objects
                     with pickle
        :return: VOID
        """
        data_serialized = pickle.dumps(data)
        client_sock.send(data_serialized)

    def threaded_client(self, conn, client_addr, func = None):
        """
        TODO: implement this method
        :param conn:
        :param client_addr:
        :return: a threaded client.
        """
        print("Thread {} started".format(client_addr[1]))
        # main logic?...
        try:
            if func:
                func(conn, client_addr)
        except Exception as e:
            print(e)
        
        # end logic
        # clean up
        del self.clients[client_addr[1]]
        print("Thread {} ended".format(client_addr[1]))