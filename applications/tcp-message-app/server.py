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
Use locks, each time a new thread is trying to write or read dat aform the server, acquire a new clients_list_lock.
Lock will be released only wen the thread finished the writing process in memory. 
Clients reading from memory do not need to be locked.

"""
import socket
import pickle
import datetime
import sys
import os
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

clients_list_lock = threading.Lock()
clients_messages_lock = threading.Lock()
server_running_lock = threading.Lock()

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
        self.clients = {} # { client_id: client_name }
        self.clients_messages = {} # {client_id: [((sender_id, sender_name),sent_on,message)]}
        self.server_running = True

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
        self.tcp_socket.close()
        # server_running_lock.acquire()
        with server_running_lock:
            self.server_running = False
        # server_running_lock.release()
        os._exit(1)

    def handle_client_get_user_list(self, client_sock, client_id, data):
        date = datetime.datetime.now()
        res = { "client_list": self.clients }
        res["client_id"] = client_id
        res["sent_on"] = date
        self.send(client_sock,res)
        log_message = "({}) List of users sent to client: {}".format(date,client_id)
        print(log_message)

    def handle_client_send_message(self, client_sock, client_id, data):
        """Parses data, saves message to user's list of messages, and returns 

        """
        res = {}
        try:
            sender_id = client_id
            sender_name = self.clients[sender_id]
            receiver_id = data["receiver_id"]
            recevier_name = self.clients[receiver_id]
            sent_on = data["sent_on"]
            message = data["message"]
            message_entry = ((sender_id, sender_name), sent_on, message)
            # with syntax makes appropriate calls to acquire and release.
            with clients_messages_lock:
                try:
                    self.clients_messages[receiver_id].append(message_entry)
                except KeyError:
                    # add entry for user
                    self.clients_messages[receiver_id] = [message_entry]

            res["message"] = "Message was successfully sent"
            
            log_message = "Message from client {} to client {} was sent".format(client_id, receiver_id)
        except KeyError as e:
            # receiver does not exist. Send response to user.
            res["message"] = "Unable to send message"
            log_message = "Unable to send message"
        date = datetime.datetime.now()
        res["client_id"] = client_id
        res["sent_on"] = date
        self.send(client_sock,res)
        print("({}) {}".format(date, log_message))

    def handle_client_get_messages(self, client_sock, client_id, data):
        """Sends client_id's messages to connected socket

        """
        res = {}
        try:
            res["client_messages"] = self.clients_messages[client_id]
            log_message = "List of messages sent to {}".format(client_id)
            num_messages = len(res["client_messages"])
            if num_messages > 0:
                res["message"] = "You have {} messages".format(num_messages)
            else:
                res["message"] = "You have no messages"
        except KeyError:
            res["client_messages"] = []
            res["message"] = "You have no messages"
            log_message = "Client {}'s messages were not found".format(client_id)
        date = datetime.datetime.now()
        res["client_id"] = client_id
        res["sent_on"] = date
        self.send(client_sock,res)
        print("({}) {}".format(date, log_message))
        

    def handle_user_disconnect(self, client_sock, client_id, data):
        raise ClientDisconnect()

    def handle_option(self, client_sock, client_id, data):
        option = data['option']
        if option == 1:
            # get user list
            return self.handle_client_get_user_list(client_sock, client_id, data)
        elif option == 2:
            # send a message
            return self.handle_client_send_message(client_sock, client_id, data)
        elif option == 3:
            # get my messages
            return self.handle_client_get_messages(client_sock, client_id, data)
        elif option == 6:
            return self.handle_user_disconnect(client_sock, client_id, data)

    def handle_client_login(self, client_sock, client_id):
        data = self.retrieve(client_sock)
        client_name = data['client_name']
        date = data['sent_on']
        # clients_list_lock.acquire()
        with clients_list_lock:
            self.clients[client_id] = client_name
        # clients_list_lock.release()
        print("({}) Client {} with clientid: {} has connected to this server".format(date, client_name, client_id))
        # prepare server response
        server_msg = "Hello from server!"
        server_response = {"client_id": client_id, "msg": server_msg, "sent_on": datetime.datetime.now()}
        # serialize and sent the data to client
        self.send(client_sock, server_response)
    
    def handle_client_disconnect(self, client_sock, client_id):
        client_name = self.clients[client_id]
        # clients_list_lock.acquire()
        with clients_list_lock:
            del self.clients[client_id]
        # clients_list_lock.release()
        client_sock.close()
        print("({}) Client {} ({}) disconnected from server".format(datetime.datetime.now(),client_name, client_id))
        # end thread
        sys.exit(0)
    
    def client_thread(self, client_sock, addr):
        # the client id assigned by server to this client
        # note that addr[0] is the host ip address
        client_id = str(addr[1])
        try:
            # inner loop handles the interaction between this client and the server
            self.handle_client_login(client_sock, client_id)
            while self.server_running:
                # the server gets data request from client
                data = self.retrieve(client_sock)
                self.handle_option(client_sock, client_id, data)
        except ClientDisconnect:
            pass
        self.handle_client_disconnect(client_sock, client_id)

    def run(self):
        try:
            self.tcp_socket.bind((self.ip, self.port)) # bind host and port to the server socket
            self.tcp_socket.listen(MAX_NUM_CONNECTIONS) # max 5 connections at a time
            print("Server listening at port: {}... ".format(str(self.port)))
            # outer loop accepts new clients
            while self.server_running:
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
        except KeyboardInterrupt:
            print("\nClosing the server")
        except ServerDisconnect:
            print("\nClosing the server")
        except Exception as e:
            print(e) # TODO: Turn to pass?
        # this happens when the server is killed. (i.e kill process from terminal )
        # or there is a non recoverable exception, and the server process is killed internally
        self.close_server()

if __name__=='__main__':
    server = Server('127.0.0.1', TEST_PORT)
    server.run()