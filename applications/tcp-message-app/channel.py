"""
The Channel class is responsible for representing a channel.
A client can create a channel, and the channel will act like a server...
"""
import socket
import pickle
import datetime
import sys
import os
import time
from helpers import (
    getIpFromUser,
    getPortFromUser,
    MAX_NUM_CONNECTIONS,
    BUFFER_SIZE,
    DisconnectSignal,
    ClientDisconnect,
    ServerDisconnect,
    TEST_PORT
)
import threading
import queue

clients_list_lock = threading.Lock()
message_queue_lock = threading.Lock()

"""
Channel subclasses client for the sockets, send, retrieve, and disconnect functionalities.
Desired inherited methods:
def send(self, data):
def retrieve(self):
"""
class Channel:
    def __init__(self):
        self.ip = getIpFromUser("Enter the ip address of the new channel: ")
        self.port = getPortFromUser("Enter the port to listen for new users: ")
        self.clients_connected = {} # contains a map of connected clients {client_id: client_socket}
        # self.client_id = None
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_queue = queue.Queue() # this holds a queue of messages to send to all users. (sender_id,message). Not a size concern because python resizes on its own.

    def retrieve(self, sock):
        # unpickles data.
        client_request = sock.recv(BUFFER_SIZE)

        if not client_request:
            raise ClientDisconnect() # error on clientside.
        # deserialize data
        client_data = pickle.loads(client_request)

        return client_data

    def send(self, sock, data):
        try:
            # pickles data for sending
            data_serialized = pickle.dumps(data)
            sock.send(data_serialized)
        except socket.error as socket_exception:
            print("Issue sending data")

    def close_server(self):
        """Closes server and stops its threads

        """
        self.tcp_socket.close()
        os._exit(1)
        
    def send_to_all(self, message, exclude_client_id=None):
        """Sends message to all clients in channel

        """
        date = datetime.datetime.now()
        res = {"sent_on": date, "message": message}
        for client_id, client_sock in self.clients_connected.items():
            if client_id is not exclude_client_id:
                self.send(client_sock, res)

    def handle_client_login(self, client_sock, client_id):
        """Logs user into channel

        """
        # send clients their client_id
        self.send(client_sock, {"client_id": client_id})
        # adds user to clients_connected map
        with clients_list_lock:
            self.clients_connected[client_id] = client_sock
        message = "Userid: {} connected to the channel".format(client_id)
        # puts message on queue to send.
        with message_queue_lock:
            self.message_queue.put((client_id, message))
        # server log message
        print(message)

    def handle_client_disconnect(self, client_sock, client_id):
        """Disconnects a client from channel

        """
        print("list of clients", self.clients_connected)
        print("key is ", client_id)
        # disconnects client
        client_sock.close()
        # delete user from clients_connected
        with clients_list_lock:
            del self.clients_connected[client_id]
        message = "Userid: {} Disconnected".format(client_id)
        # notify all clients
        with message_queue_lock:
            self.message_queue.put((client_id, message))
        # print server log message
        print(message)
    
    def client_thread(self, client_sock, addr):
        # read in client's login handshake.
        data = self.retrieve(client_sock)
        client_id = str(addr[1])
        try:
            # logs client in
            self.handle_client_login(client_sock, client_id)
            while True:
                # the server gets data request from client
                data = self.retrieve(client_sock)
                # extract message from data
                try:
                    client_id = data["client_id"]
                    client_name = data["client_name"]
                    message = data["message"]
                    broadcast_message = "{}: {}".format(client_name, message)
                    with message_queue_lock:
                        # adds message to queue to broadcast to all clients
                        self.message_queue.put((client_id, broadcast_message))
                except KeyError:
                    # error in request.
                    pass
        except ClientDisconnect:
            pass
        self.handle_client_disconnect(client_sock, client_id)

    def broadcast_thread(self):
        """Reads from a message queue and sends a message to all clients when new message comes
         from queue

        """
        # poll for new messages
        while True:
            with message_queue_lock:
                # grabs message from queue
                # note .get() innately waits for next message on queue... no need for sleep
                sender_id, message = self.message_queue.get()
            # sends to all, excluding the sender of the message so no dups on sender's side
            self.send_to_all(message, sender_id)
            # after sending all, remove message from queue
                
    def run_server(self):
        """Main server logic

        """
        # this thread handles broadcasting to clients.
        thread_bc = threading.Thread(target=self.broadcast_thread)
        thread_bc.start()
        while True:
            # accept new client
            client_sock, addr = self.tcp_socket.accept()
            # this thread handles interaction with clients
            thread_c = threading.Thread(target=self.client_thread, args=(client_sock, addr))
            thread_c.start()
            

    def run(self):
        try:
            self.tcp_socket.bind((self.ip, self.port)) # bind host and port to the server socket
            self.tcp_socket.listen(MAX_NUM_CONNECTIONS) # max 5 connections at a time
            print("Channel Info")
            print("IP Address :", self.ip)
            print("Channel id:", self.port)
            print("Waiting for users....")
            # outer loop accepts new clients
            self.run_server()
        except socket.error as socket_exception:
            print(socket_exception) # An exception ocurred at this point
        except KeyboardInterrupt:
            print("\nClosing the channel")
        except ServerDisconnect:
            print("\nClosing the channel")
        except Exception as e:
            print(e) # TODO: Turn to pass?
        # this happens when the server is killed. (i.e kill process from terminal )
        # or there is a non recoverable exception, and the server process is killed internally
        self.close_server()