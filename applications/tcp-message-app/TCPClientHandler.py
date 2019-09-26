"""
Basic TCP Client code sample.
This client creates a connection to the server,
and then, sends serialized data. The server, then
provides a response that is printed in console
"""
# The only socket library allowed for this assigment
import socket
import pickle

class TCPClientHandler(object):
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