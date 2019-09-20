"""
Basic TCP Client code sample.
This client creates a connection to the server,
and then, sends serialized data. The server, then
provides a response that is printed in console
"""
# The only socket library allowed for this assigment
import socket
import pickle
import datetime
HOST = '127.0.0.1' # The server IP address. Use localhost for this project
PORT = 65432
# The server port
try:
    # Creates the client socket
    # AF_INET refers to the address family ipv4.
    # The SOCK_STREAM means connection oriented TCP protocol.
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connects to the server using its host IP and port
    client.connect((HOST, PORT))
    # Prepare, serializes and send data to the server
    data = {"msg_from_client": "Hello from Client!", "sent_on": datetime.datetime.now()}
    data_serialized = pickle.dumps(data)
    client.send(data_serialized)
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