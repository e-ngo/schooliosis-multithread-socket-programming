"""
Basic TCP Client code sample.
This client creates a connection to the server,
and then, sends serialized data. The server, then
provides a response that is printed in console
"""
# The only socket library allowed for this assigment
import socket
import pickle

class TCPClientHandler:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # The server port
        # Creates the client socket
        # AF_INET refers to the address family ipv4.
        # The SOCK_STREAM means connection oriented TCP protocol.
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def test(self):
        print("Host and port", self.host, self.port)

    def handler_send(self, data):
        """Prepare, serializes and send data to the server

        """
        data_serialized = pickle.dumps(data)
        self.tcp_socket.send(data_serialized)

    def handler_get(self):
        """Retrieves response from server and parses output

        """
        # Server response is received. However, we need to take care of data size
        server_response = self.tcp_socket.recv(4096)
        # Desearializes the data.
        server_data = pickle.loads(server_response)
        # Get all the values in the data dictionary
        client_id = server_data['client_id'] # the client id assigned by the server
        server_msg = server_data['msg']
        return (client_id, server_msg)

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
        try:
            # Connects to the server using its host IP and port
            # tcp_socket.connect((self.host, self.port))
            # Connects to the server using its host IP and port
            # client.connect((HOST, PORT))
            # # Prepare, serializes and send data to the server
            # data = {"msg_from_client": "Hello from Client!", "sent_on": datetime.datetime.now()}
            # data_serialized = pickle.dumps(data)
            # client.send(data_serialized)
            # Server response is received. However, we need to take care of data size
            server_response = client.recv(4096)
            # Desearializes the data.
            server_data = pickle.loads(server_response)
            # Get all the values in the data dictionary
            client_id = data['client_id'] # the client id assigned by the server
            server_msg = data['msg_from_server']
            # Print data and close client.
            # What would be needed in order to keep the client alive all the time?
            # Think about it
            print("Client " + str(client_id) + "successfully connected to server")
            print("Server says: " + server_msg)
        except socket.error as socket_exception:
            print(socket_exception) # An exception ocurred at this point
        client.close()
    def start(self):
        # establish connection with server
        self.client.connect()

        # Logs in to server.
        # client_msg = ("0", self.client_name)
        client_msg = self.client.client_name
        data = {"msg": client_msg, "sent_on": datetime.datetime.now(), "client_id": None, "option": -1}
        self.handler_send(data)
        response = self.handler_get()
        self.client_id = response["client_id"]
        print("Successfully connected to server with IP: {} and port: {}".format(self.ip, self.port))
        print("Your client info is:")
        print("Client Name: ", self.client_name)
        print("Client ID: ", self.client_id)

        print(response[msg])#debug