"""

a.) TCP Client in charge of
1.) Connect to server
2.) Send requests to the server
3.) Retrieve responses from the server.
Retrieved responses from the server are handeld by TCPClientHandler, 
    which is the worker class that provides all the menu actions executed from client size.
b.) after executing client.py script, should show a menu where user can select different actions.
c.) Options

Design:

Class client:


"""
from helpers import (
    getIpFromUser,
    getPortFromUser,
    DisconnectSignal
)
import socket
import datetime
from TCPClientHandler import TCPClientHandler

# def SocketOperationHandler(func):
#     def wrapper(*args, **kwargs):
#         try:
#             func(*args, **kwargs)
#         except socket.error as socket_exception:
#             print(socket_exception)
#         self.socket.close()
#     return wrapper

class Client(TCPClientHandler):

    def __init__(self, ip=None, port=None):
        if not ip:
            # Prompt user for IP
            ip = getIpFromUser("Enter the server IP Address: ")
        if not port:
            # Prompt user for port
            port = getPortFromUser("Enter the server port:")
        # super(Client, self).__init__(host=ip, port=port) # python2 compat
        # 
        self.client_name = input("Your id key (i.e your name): ")
        self.client_id = None
        super().__init__(ip, port)

    def connect(self):
        """Connects to the server
        
        """
        # Connects to the server using its host IP and port
        self.tcp_socket.connect((self.host, self.port))

        # Logs in to server.
        # client_msg = ("0", self.client_name)
        client_msg = self.client_name
        data = {"msg": client_msg, "sent_on": datetime.datetime.now(), "client_id": None}
        self.handler_send(data)
        response = self.handler_get()
        self.client_id = response["client_id"]
        print("Successfully connected to server with IP: {} and port: {}".format(self.ip, self.port))
        print("Your client info is:")
        print("Client Name: ", self.client_name)
        print("Client ID: ", self.client_id)

        print(response[msg])#debug
        
    def _disconnect(self):
        self.tcp_socket.close()
        
    def send(self, data):
        """send requests to the server

        """
        
        self.handler_send(data)

    def get(self):
        """retrieve responses from the server

        """
        pass

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
        6. Diconnect from server
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
        data = ("1","")
        self.handler_send(data)
        (client_id, client_list) = self.handler_get()
        print("Client List")
        for i in client_list:
            print(i, ": ", client_list[i])

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
            self.connect()
            while True:
                self.print_menu()
                option = self.get_menu_option()
                self.handle_menu_option(option)

        except socket.error as socket_exception:
            print(socket_exception) # An exception ocurred at this point
        except DisconnectSignal:
            print("Client Disconnected!")
        self._disconnect()

if __name__ == '__main__':
    client = Client()
    client.run()
    client.disconnect()