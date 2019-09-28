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
    MAX_NUM_CONNECTIONS,
    BUFFER_SIZE
)
import threading

lock = threading.Lock()

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
        self.clients = {}

    def retrieve(self, sock):
        # try:

        # except EOFError:
            # TODO: FIX THIS. HOW TO HANDLE PICKLE LOADS PROPERLY?
            # pass
        # unpickles data.
        client_request = sock.recv(BUFFER_SIZE)
        # deserialize data
        client_data = pickle.loads(client_request)

        return client_data

    def send(self, sock, data):
        # pickles data for sending
        data_serialized = pickle.dumps(data)
        sock.send(data_serialized)

    def handle_client_get_user_list(self, data):
        print("Clients list retrieved") # TODO: Make log more verbose
        return { "client_list": self.clients }

    def handle_client_send_message(self, data):
        pass

    def handle_client_get_messages(self, data):
        pass

    def handle_user_disconnect(self, data):
        pass

    def handle_option(self, data):
        option = data['option']
        if option == 1:
            # get user list
            return self.handle_client_get_user_list(data)
        elif option == 2:
            # send a message
            return self.handle_client_send_message(data)
        elif option == 3:
            # get my messages
            return self.handle_client_get_messages(data)
        elif option == 6:
            return self.handle_user_disconnect(data)
            # Create a new channel
            # return self.handle_client_create_channel()
        # elif option == 5:
            # Chat in a new channel with your friends
            # return self.handle_client_join_new_channel()

    def handle_client_login(self, client_sock, client_id):
        data = self.retrieve(client_sock)
        client_name = data['client_name']
        date = data['sent_on']
        lock.acquire()
        self.clients[client_id] = client_name
        lock.release()
        print("({}) Client {} with clientid: {} has connected to this server".format(date, client_name, client_id))
        # prepare server response
        server_msg = "Hello from server!"
        server_response = {"client_id": client_id, "msg": server_msg, "sent_on": datetime.datetime.now()}
        # serialize and sent the data to client
        self.send(client_sock, server_response)
    
    def client_thread(self, client_sock, addr):
        # the client id assigned by server to this client
        # note that addr[0] is the host ip address
        client_id = addr[1]
        # inner loop handles the interaction between this client and the server
        self.handle_client_login(client_sock, client_id)
        while True:
            # the server gets data request from client
            data = self.retrieve(client_sock)

            res = self.handle_option(data)
            res["client_id"] = client_id
            res["sent_on"] = datetime.datetime.now()

            self.send(client_sock,res)
            print("All sent!") # DEBUG

        print("Disconnecting client {} {}".format(self.clients[client_id], client_id))
        client_sock.close()

    def run(self):
        try:
            self.tcp_socket.bind((self.ip, self.port)) # bind host and port to the server socket
            self.tcp_socket.listen(MAX_NUM_CONNECTIONS) # max 5 connections at a time
            print("Server listening at port: {}... ".format(str(self.port)))
            # outer loop accepts new clients
            while True:
                # saves the host ip address and the client socket connected
                client_sock, addr = self.tcp_socket.accept()
                # # keep the server alive waiting for clients
                # client connected, server accepts connection
                thread = threading.Thread(target=self.client_thread, args=(client_sock, addr))
                thread.start()
                # this happens when either the client do no send more data
                # or the client closed the connection from the client side.
                
        except socket.error as socket_exception:
            print(socket_exception) # An exception ocurred at this point
        except Exception as e:
            print(e) # TODO: Turn to pass?
        # this happens when the server is killed. (i.e kill process from terminal )
        # or there is a non recoverable exception, and the server process is killed internally
        self.tcp_socket.close()

if __name__=='__main__':
    server = Server('127.0.0.1', 50000)
    server.run()