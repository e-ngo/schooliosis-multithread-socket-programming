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
)
import threading
import queue

# lock used for writing to Channel.clients_connected
clients_list_lock = threading.Lock()
# lock used for writing to message queue
message_queue_lock = threading.Lock()

class Channel:
    """
    Channel allows clients to connect to it and chat with each other
    """
    def __init__(self):
        self.ip = getIpFromUser("Enter the ip address of the new channel: ")
        self.port = getPortFromUser("Enter the port to listen for new users: ")
        self.clients_connected = {} # contains a map of connected clients {client_id: client_socket}
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_queue = queue.Queue() # this holds a queue of messages to send to all users. (sender_id,message). Not a size concern because python resizes on its own.

    def retrieve(self, sock):
        """Retrieves a message from client

        """
        # unpickles data.
        client_request = sock.recv(BUFFER_SIZE)

        if not client_request:
            raise ClientDisconnect() # error on clientside.
        # deserialize data
        client_data = pickle.loads(client_request)

        return client_data

    def send(self, sock, data):
        """Sends message to client

        """
        # pickles data for sending
        data_serialized = pickle.dumps(data)
        sock.send(data_serialized)

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
        # for each client in channel
        for client_id, client_sock in self.clients_connected.items():
            # if client is not excluded client
            if client_id != exclude_client_id:
                # send message
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
        # puts new user connected message in queue
        with message_queue_lock:
            self.message_queue.put((client_id, message))

    def handle_client_disconnect(self, client_sock, client_id):
        """Disconnects a client from channel

        """
        # disconnects client
        client_sock.close()
        # delete user from clients_connected
        with clients_list_lock:
            del self.clients_connected[client_id]
        message = "Userid: {} Disconnected".format(client_id)
        # notify all clients
        with message_queue_lock:
            self.message_queue.put((client_id, message))
    
    def client_thread(self, client_sock, addr):
        """This thread handles connection with new client

        """
        # read in client's login handshake.
        data = self.retrieve(client_sock)
        client_id = str(addr[1])
        try:
            # logs client in
            self.handle_client_login(client_sock, client_id)
            while True:
                # constantly listen for client's message
                data = self.retrieve(client_sock)
                try:
                    # extract message from data
                    client_id = data["client_id"]
                    client_name = data["client_name"]
                    message = data["message"]
                    broadcast_message = "{}: {}".format(client_name, message)
                    with message_queue_lock:
                        # adds message to queue to broadcast to all clients
                        self.message_queue.put((client_id, broadcast_message))
                except KeyError:
                    # error in request...
                    pass
        except ClientDisconnect:
            # if ClientDisconnect signal was raised, end connection
            pass
        # disconnects client
        self.handle_client_disconnect(client_sock, client_id)

    def broadcast_thread(self):
        """This thread reads from a message queue and sends a message to all clients when new message comes from queue

        """
        # poll for new messages
        while True:
            try:
                with message_queue_lock:
                    # grabs message from queue
                    sender_id, message = self.message_queue.get(block=False)
                # sends to all, excluding the sender of the message so no dups on sender's side
                self.send_to_all(message, sender_id)
                #server log message
                print(message)
            except queue.Empty:
                # if queue is empty, wait
                time.sleep(0.10)
                
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
        """Initializes server configurations. Starts server

        """
        try:
            self.tcp_socket.bind((self.ip, self.port)) # bind host and port to the server socket
            self.tcp_socket.listen(MAX_NUM_CONNECTIONS)
            print("Channel Info")
            print("IP Address :", self.ip)
            print("Channel id:", self.port)
            print("Waiting for users....")
            # starts server logic
            self.run_server()
        except socket.error as socket_exception:
            print(socket_exception)
        except KeyboardInterrupt:
            # allows user to kill process with ctrl-c
            print("\nClosing the channel")
        except ServerDisconnect:
            print("\nClosing the channel")
        except Exception as e:
            pass
        # Closes server
        self.close_server()