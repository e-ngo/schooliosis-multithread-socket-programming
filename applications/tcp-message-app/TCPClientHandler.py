"""
Basic TCP Client code sample.
This client creates a connection to the server,
and then, sends serialized data. The server, then
provides a response that is printed in console
"""
# The only socket library allowed for this assigment
import socket
import datetime
from helpers import (
    DisconnectSignal
)
class TCPClientHandler:
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
        """Retrieve responses from the server

        """
        while True:
            option = int(input("Your option <enter a number>: "))
            if 1 <= option <= 6:
                return option

    def get_user_list(self):
        """Gets a list of active users from server.

        """
        data = {"sent_on": datetime.datetime.now(), "client_id": self.client.client_id, "option": 1}
        self.client.send(data)
        response = self.client.retrieve()
        client_list = response["client_list"]
        print("Client List:")
        num = 1
        for client_id, client_name in client_list.items():
            print("({}) {} : {}".format(num, client_name, client_id))

    def send_message(self):
        """Sends a message

        """
        pass

    def get_messages(self):
        """Retrieves user's messages

        """
        pass

    def create_new_channel(self):
        """Creates a new channel

        """
        pass

    def join_new_channel(self):
        """Joins an existing p2p channel

        """
        pass

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
            raise DisconnectSignal()



    def run(self):
        """Runs the client

        """
        try:
            # establish connection with server
            self.client.connect()

            # Logs in to server.
            data = {"client_name": self.client.client_name, "sent_on": datetime.datetime.now(), "client_id": None, "option": -1}
            self.client.send(data)
            response = self.client.retrieve()
            self.client.client_id = response["client_id"]
            print("Successfully connected to server with IP: {} and port: {}".format(self.client.ip, self.client.port))
            print("Your client info is:")
            print("Client Name: ", self.client.client_name)
            print("Client ID: ", self.client.client_id)

            # 'start' client
            while True:
                self.print_menu()
                option = self.get_menu_option()
                self.handle_menu_option(option)
            
        except socket.error as socket_exception:
            print(socket_exception) # An exception ocurred at this point
        except DisconnectSignal:
            print("Client Disconnected!")
        except Exception as e:
            print(e)
        self.client.disconnect()
        