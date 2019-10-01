"""
This module implements the Server class
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
)
import threading

# this lock is for Server.clients
clients_list_lock = threading.Lock()
# this lock is for server.clients_messages
clients_messages_lock = threading.Lock()
# this lock is for Server.server_running
server_running_lock = threading.Lock()

class Server:
    """The Server class interfaces with the TCPClientHandler to create a tcp-message-app.

    """
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
        self.clients = {} # Holds all clients { client_name: (password,client_sock) }
        self.clients_messages = {} # Holds all client's messages {client_id: [(sender_id,sent_on,message)]}
        self.server_running = True # signals whether or not server is running

    def retrieve(self, sock):
        """Handles receiving client request from socket.

        """
        # unpickles data.
        client_request = sock.recv(BUFFER_SIZE)

        if not client_request:
            # error on clientside. Disconnect client.
            raise ClientDisconnect()
        # deserialize data
        client_data = pickle.loads(client_request)

        return client_data

    def send(self, sock, data):
        """Handles serializing and sending data to clients

        """
        try:
            # pickles data for sending
            data_serialized = pickle.dumps(data)
            sock.send(data_serialized)
        except socket.error as socket_exception:
            print("Issue sending data")

    def close_server(self):
        """Closes the listening socket and ends process

        """
        self.tcp_socket.close()
        with server_running_lock:
            # signal to other threads to end
            self.server_running = False
        # ends process
        os._exit(1)

    def handle_client_get_user_list(self, client_sock, client_id, data):
        """Sends user list to client

        """
        # generate response
        date = datetime.datetime.now()
        clients_list = []
        for name, sock in self.clients.items():
            clients_list.append(name)
        res = { "client_list": clients_list }
        res["client_id"] = client_id
        res["sent_on"] = date
        # send response
        self.send(client_sock,res)
        # print server log message
        log_message = "({}) List of users sent to client: {}".format(date,client_id)
        print(log_message)

    def handle_client_send_message(self, client_sock, client_id, data):
        """Parses data, saves message to user's list of messages, and returns message code.

        """
        res = {} # holds response object
        try:
            # get message information
            sender_id = client_id
            receiver_id = data["receiver_id"]
            sent_on = data["sent_on"]
            message = data["message"]
            message_entry = (sender_id, sent_on, message)
            # with syntax makes appropriate calls to acquire and release.
            with clients_messages_lock:
                # save message on server for respective receiver
                try:
                    # if recevier key exists in object, add to existing list of messages
                    self.clients_messages[receiver_id].append(message_entry)
                except KeyError:
                    #  else, add entry for user
                    self.clients_messages[receiver_id] = [message_entry]
            # response success message
            res["message"] = "Message was successfully sent"
            # server log message
            log_message = "Message from client {} to client {} was sent".format(client_id, receiver_id)
        except KeyError as e:
            # receiver does not exist. Send response to user.
            res["message"] = "Unable to send message"
            log_message = "Unable to send message"
        date = datetime.datetime.now()
        res["client_id"] = client_id
        res["sent_on"] = date
        self.send(client_sock,res)
        # print server log message
        print("({}) {}".format(date, log_message))

    def handle_client_get_messages(self, client_sock, client_id, data):
        """Sends client's messages to client

        """
        res = {}
        try:
            # Get client's messages
            res["client_messages"] = self.clients_messages[client_id]
            log_message = "List of messages sent to {}".format(client_id)
            num_messages = len(res["client_messages"])
            if num_messages > 0:
                res["message"] = "You have {} messages".format(num_messages)
            else:
                res["message"] = "You have no messages"
        except KeyError:
            # if client has no entry, respond with error
            res["client_messages"] = []
            res["message"] = "You have no messages"
            log_message = "Client {}'s messages were not found".format(client_id)
        # format and send response
        date = datetime.datetime.now()
        res["client_id"] = client_id
        res["sent_on"] = date
        self.send(client_sock,res)
        # print server debug message
        print("({}) {}".format(date, log_message))

    def handle_user_disconnect(self, client_sock, client_id, data):
        """Handles option to disconnect client

        """
        # raises a signal that is caught by server and ends client connection
        raise ClientDisconnect()

    def handle_option(self, client_sock, client_id, data):
        """Calls proper handling function based off of option

        """
        # get option from client request
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
            # disconnect client
            return self.handle_user_disconnect(client_sock, client_id, data)

    def handle_client_login(self, client_sock):
        """Logs client into server by creating entries in self.clients and self.clients_messages and responding with user's client_id

        """
        # get client information
        data = self.retrieve(client_sock)
        client_id = data['client_name']
        date = data['sent_on']
        password = data['password']
        try:
            # if user exists...
            while True:
                # compares password field in stored client to given password
                if self.clients[client_id][0] == password:
                    # password matches
                    break
                # password does not match. Notify client to try again...
                self.send(client_sock, {"success": False, "message": "Incorrect Password!"})
                password_entry = self.retrieve(client_sock)
                password = password_entry['password']
        except KeyError:
            # user does not exist. create new user.
            pass
        # regsiters user with client_sock. (Essentially creates new user in db)
        with clients_list_lock:
            # creates new client entry
            self.clients[client_id] = (password, client_sock)
        # prepare server response
        server_response = {"client_id": client_id, "success": True, "sent_on": datetime.datetime.now()}
        # sends client_id to user
        self.send(client_sock, server_response)
        # print debug message
        print("({}) Client {} has connected to this server".format(date, client_id))

        return client_id
    
    def handle_client_disconnect(self, client_sock, client_id):
        """Disconnects client from server. Removes client's information from server.

        """
        client_sock.close()
        print("({}) Client {} disconnected from server".format(datetime.datetime.now(),client_id))
        # end thread
        sys.exit(0)
    
    def client_thread(self, client_sock, addr):
        """Client thread handles interaction with specific client given socket

        """
        client_id = ""
        try:
            # log user in to server. get client_id, which is the client's name.
            client_id = self.handle_client_login(client_sock)
            # constantly poll for new request
            while self.server_running:
                # the server gets data request from client
                data = self.retrieve(client_sock)
                # server handles option
                self.handle_option(client_sock, client_id, data)
        except ClientDisconnect:
            # if ClientDisconnect signal has been raised...
            pass
        # disconnect client
        self.handle_client_disconnect(client_sock, client_id)

    def run(self):
        """Starts running the server

        """
        try:
            # binds to socket
            self.tcp_socket.bind((self.ip, self.port)) # bind host and port to the server socket
            self.tcp_socket.listen(MAX_NUM_CONNECTIONS) # Allow max 5 buffer connection requests at a time
            # server debug message
            print("Server listening at port: {}... ".format(str(self.port)))
            # Constantly accepts new clients
            while self.server_running:
                # saves the host ip address and the client socket connected
                client_sock, addr = self.tcp_socket.accept()
                # creates new thread to handle new client
                thread = threading.Thread(target=self.client_thread, args=(client_sock, addr))
                thread.start()
        except socket.error as socket_exception:
            print(socket_exception)
        except KeyboardInterrupt:
            # allows ctrl-c to exit program
            print("\nClosing the server")
        except ServerDisconnect:
            print("\nClosing the server")
        except Exception as e:
            pass
        # close server
        self.close_server()

if __name__=='__main__':
    server = Server()
    server.run()