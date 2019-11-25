# -*- coding: utf-8 -*-
""" The server
This file has the class client that implements a server socket.
Note that you can replace this server file by your server from
assignment #1.
"""
import socket
import pickle
import threading

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

    def listen(self):
        """
        TODO: implement this method
        Listen for new connections
        :return: VOID
        """
        try:
            # associate the socket to host and port
            server_socket.bind((self.host_ip, self.host_port))
            # listen and accept clients
            server_socket.listen()
            print(f"Server started\nListening at {self.HOST}({self.PORT}):")
            while True:
                self.accept()
            
        except socket.error as sock_error:
            print(sock_error)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print("An exception has occurred", e)

        server_socket.close()
        print("Closing the server")
        os._exit(0)

    def accept(self):
        """
        TODO: implement this method
        Accept new clients
        :return:
        """
        client_sock, addr = self.server_socket.accept()
        self.clients[addr[1]] = client_sock
        print(f"Client {addr} has connected!")
        thread = threading.Thread(target=self.threaded_client, args=(client_sock, addr))
        thread.start()

    def receive(self, memory_allocation_size):
        """
        TODO: implement this method
        Receives data from clients socket
        :param memory_allocation_size:
        :return: deserialized data
        """
        self.client.settimeout(self.KEEP_ALIVE_TIME)
        client_request = self.client.recv(self.BUFFER_SIZE)
        if not client_request:
            raise ClientDisconnect()
        # Deserializes the data.
        client_data = pickle.loads(client_request)
        return client_data

    def send(self, data):
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
        self.client.send(data_serialized)

    def threaded_client(self, conn, client_addr):
        """
        TODO: implement this method
        :param conn:
        :param client_addr:
        :return: a threaded client.
        """
        print("Thread {} started".format(client_addr[1]))
        # main logic?...
        try:
            pass
        except Exception as e:
            print(e)
        
        # end logic
        # clean up
        del self.clients[client_addr[1]]
        print("Thread {} ended".format(client_addr[1]))



