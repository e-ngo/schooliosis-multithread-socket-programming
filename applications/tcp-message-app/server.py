"""
Low level implementation of a single instance TCP Server using sockets.
Note that for your project, your server code needs to be object oriented designed,
scalable, and the server must accept multiple clients at the same time
using multithreading and locks.

TCP Server should be implemented as follows:
1.) Currently main thread is blocking. When a client connects, they will get the main thread,
and will wait until server provides a response. Need to implement multi-threading to avoid
this situation. Each new client connection generates a new thread.
"May face race conditions. Solved with locks and mutex".
tw othreads may try to write at the same time on the server (trying to write to the same memory slot).
Use locks, each time a new thread is trying to write or read dat aform the server, acquire a new lock.
Lock will be released only wen the thread finished the writing process in memory. 
Clients reading from memory do not need to be locked.

"""
import socket
import pickle
import datetime
from helpers import (
    getIpFromUser,
    getPortFromUser,
)
# HOST = "127.0.0.1" # running in localhost
# PORT = 65432 # server will be listening at this port
MAX_NUM_CONNECTIONS = 5
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # server socket


# This port range is considered safe to use by IANA
class Server:
    def __init__(self, ip=None, port=None):
        self.ip = ip
        self.port = port
        if not ip:
            # Prompt user for IP
            self.ip = getIpFromUser("Enter the server IP Address: ")
        if not port:
            # Prompt user for port
            self.port = getPortFromUser("Enter the server port:")

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def handle_request(self):
        # unpickles data.
        client_request = self.tcp_socket.recv(4096)
        # deserialize data
        client_data = pickle.loads(client_request)

        return client_data

    def handle_send(self, data):
        # pickles data for sending
        data_serialized = pickle.dumps(data)
        self.tcp_socket.send(data_serialized)
    

    def run(self):
        try:
            self.tcp_socket.bind((self.ip, self.port)) # bind host and port to the server socket
            self.tcp_socket.listen(MAX_NUM_CONNECTIONS) # max 5 connections at a time
            print("Server listening at port: " + str(self.port) + "... ")
            # outer loop accepts new clients
            while True:
                # # keep the server alive waiting for clients
                # client connected, server accepts connection
                # saves the host ip address and the client socket connected
                client_sock, addr = self.tcp_socket.accept()
                # the client id assigned by server to this client
                # note that addr[0] is the host ip address
                client_id = addr[1]
                print("Client " + str(client_id) + " has connected")
                # inner loop handles the interaction between this client and the server
                while True:
                    # the server gets data request from client
                    request_from_client = client_sock.recv(4096)
                    # deserializes the data
                    data = pickle.loads(request_from_client)
                    # now the data is disponible to be used by server
                    client_msg = data['msg']
                    date = data['sent_on']
                    print("Client says: " + client_msg + " message sent on " + str(date))
                    # prepare server response
                    server_msg = "Hello from server!"
                    server_response = {"client_id": client_id, "msg": server_msg}
                    # serialize and sent the data to client
                    serialized_data = pickle.dumps(server_response)
                    client_sock.send(serialized_data)
                # this happens when either the client do no send more data
                # or the client closed the connection from the client side.
                client_sock.close()
        except socket.error as socket_exception:
            print(socket_exception) # An exception ocurred at this point
        # this happens when the server is killed. (i.e kill process from terminal )
        # or there is a non recoverable exception, and the server process is killed internally
        self.tcp_socket.close()

if __name__=='__main__':
    server = Server()
    server.run()

"""
Notes: client messages are in the form:
{"msg_from_client": (option, data), "sent_on": datetime.datetime.now()}

"""