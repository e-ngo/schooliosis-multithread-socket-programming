"""
Retrieved responses from the server are handeld by TCPClientHandler, 
    which is the worker class that provides all the menu actions executed from client size.
"""
import socket
import datetime
from helpers import (
    DisconnectSignal,
    ServerDisconnect,
    ClientDisconnect,
    getIpFromUser,
    getPortFromUser
)
import threading
import os

from client import Client
from channel import Channel

socket_lock = threading.Lock()
class TCPClientHandler:
    """TCPClientHandler acts as the worker class that implements all the menu actions, 
    executed using the client class

    """
    def __init__(self, client):
        self.client = client

    def print_menu(self):
        """Prints menu option to console

        """
        print("""
        ****** TCP Message App ******
        -----------------------
        Options Available:
        1. Get user list
        2. Sent a message
        3. Get my messages
        4. Create a new channel
        5. Chat in a channel with your friends
        6. Disconnect from server
        """)

    def get_menu_option(self):
        """Gets menu option from user

        """
        while True:
            option = int(input("Your option <enter a number>: "))
            if 1 <= option <= 6:
                return option

    def get_user_list(self):
        """Gets a list of active users from server.

        """
        # format request
        data = {"sent_on": datetime.datetime.now(), "client_id": self.client.client_id, "option": 1}
        self.client.send(data)
        response = self.client.retrieve()

        client_list = response["client_list"]
        print("Client List:")
        for num in range(len(client_list)):
            print("({}) {}".format(num + 1, client_list[num]))

    def send_message(self):
        """Sends a message to another client on server

        """
        # get client message and receiver information
        message = input("Your message: ")
        receiver_id = input("User ID recipient: ")
        # format request
        data = {"sent_on": datetime.datetime.now(), "client_id": self.client.client_id, "option": 2}
        data["message"] = message
        data["receiver_id"] = receiver_id
        self.client.send(data)
        response = self.client.retrieve()
        print(response["message"])

    def get_messages(self):
        """Retrieves client's messages from server

        """
        data = {"sent_on": datetime.datetime.now(), "client_id": self.client.client_id, "option": 3}
        self.client.send(data)
        response = self.client.retrieve()
        print(response["message"])
        for i in response["client_messages"]:
            # API response: (sender_id,sent_on,message)
            # prints: (sent_on) sender_name says message
            print("({}) {} says {}".format(i[1],i[0],i[2]))

    def create_new_channel(self):
        """Creates a new channel

        """
        # close current connection
        self.client.disconnect()

        channel = Channel()
        channel.run()

    def client_receive_thread(self):
        """Thread that receives messages from the server/channel
        
        """
        # constantly poll for new messages
        try:
            while True:
                # receive message from server
                data = self.client.retrieve()
                message = data["message"]
                # print message
                print(message)
        except ServerDisconnect:
            # signaled that server has closed the connection.
            print("Server Disconnected!")
            self.client.disconnect()
            # end process
            os._exit(1)

    def client_send_thread(self):
        """Thread that sends messages from the server
        
        """
        print("Enter Bye to exit the channel")
        try:
            # constantly poll for user input.
            while True:
                # get input from user
                message = input()
                # format request
                request = {"client_id":self.client.client_id, "client_name": self.client.client_name, "message": message}
                self.client.send(request)
                # if message has Bye, end execution
                if "Bye" in message:
                    # disconnect client
                    break
        except KeyboardInterrupt:
            # allows user to exit with ctrl-c without an ugly exception message
            pass
        # if control flow reaches this point, close client...
        raise ClientDisconnect()

    def join_new_channel(self):
        """Join an existing channel

        """
        try:
            # close current connection
            self.client.disconnect()
            # get new channel information
            ip = getIpFromUser("Enter the ip address of the channel: ")
            port = getPortFromUser("Enter the port of the channel: ")
            name = self.client.client_name
            # create new client.
            self.client = Client(ip, port, name)
            # connects the client to channel
            self.client.connect()
            # Logs in to channel.
            data = {"client_name": self.client.client_name, "sent_on": datetime.datetime.now(), "client_id": None }
            # sends login handshake
            self.client.send(data)
            # get client_Id.
            response = self.client.retrieve()
            self.client.client_id = response["client_id"]
            # thread to receive messages and print them
            thread_receive = threading.Thread(target=self.client_receive_thread)
            thread_receive.start()
            # thread to send messages. Main thread.
            self.client_send_thread()
        except Exception:
            # if uncaught exception, catch it here and disconnect client
            print("Connection has closed")
            raise ClientDisconnect()

    def handle_menu_option(self, option):
        """Handles user option

        """
        if option == 1:
            # get user list
            return self.get_user_list()
        elif option == 2:
            # send a message
            return self.send_message()
        elif option == 3:
            # get my messages
            return self.get_messages()
        elif option == 4:
            # Create a new channel
            return self.create_new_channel()
        elif option == 5:
            # Chat in a new channel with your friends
            return self.join_new_channel()
        elif option == 6:
            # Disconnect from server
            raise ClientDisconnect()

    def run(self):
        """Runs the client

        """
        try:
            # establish connection with server
            self.client.connect()
            response = None
            # queries client for username
            while True:
                # Logs in to server.
                password = input("Password for {}: ".format(self.client.client_name))
                data = {"client_name": self.client.client_name, "sent_on": datetime.datetime.now(), "password": password}
                self.client.send(data)
                # retrieve client_id from server
                response = self.client.retrieve()
                if response["success"] == True:
                    break
                print(response["message"])

            self.client.client_id = response["client_id"]
            print("Successfully connected to server with IP: {} and port: {}".format(self.client.ip, self.client.port))
            print("Your client info is:")
            print("Client Name: ", self.client.client_name)
            print("Client ID: ", self.client.client_id)
            
            # constantly poll for input
            while True:
                self.print_menu()
                option = self.get_menu_option()
                self.handle_menu_option(option)
            
        except socket.error as socket_exception:
            print(socket_exception)
        except ClientDisconnect:
            print("Client Disconnected!")
        except ServerDisconnect:
            print("Server Disconnected!")
        except Exception as e:
            # if any other uncaught exception
            pass
        # if control flow reaches here, disconnect client.
        self.client.disconnect()
        # end process
        os._exit(1)