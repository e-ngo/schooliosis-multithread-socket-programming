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
import helpers
# HOST = "127.0.0.1" # running in localhost
# PORT = 65432 # server will be listening at this port
# MAX_NUM_CONNECTIONS = 5
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # server socket
# server.bind((self.host, self.port)) # bind host and port to the server socket
# server.listen(MAX_NUM_CONNECTIONS) # max 5 connections at a time
# print("Server listening at port: " + str(PORT) + "... ")
# # keep the server alive waiting for clients
# while True:
#     # outer loop accepts new clients
#     try:
#         # client connected, server accepts connection
#         # saves the host ip address and the client socket connected
#         client_sock, addr = server.accept()
#         # the client id assigned by server to this client
#         # note that addr[0] is the host ip address
#         client_id = addr[1]
#         print("Client " + str(client_id) + " has connected")
#         # inner loop handles the interaction between this client and the server
#         while True:
#             # the server gets data request from client
#             request_from_client = client_sock.recv(4096)
#             # deserializes the data
#             data = pickle.loads(request_from_client)
#             # now the data is disponible to be used by server
#             client_msg = data['msg_from_client']
#             date = data['sent_on']
#             print("Client says: " + client_msg + " message sent on " + str(date))
#             # prepare server response
#             server_msg = "Hello from server!"
#             server_response = {"client_id": client_id, "msg_from_server": server_msg}
#             # serialize and sent the data to client
#             serialized_data = pickle.dumps(server_response)
#             client_sock.send(serialized_data)
#         # this happens when either the client do no send more data
#         # or the client closed the connection from the client side.
#         client_sock.close()
#     except socket.error as socket_exception:
#         print(socket_exception) # An exception ocurred at this point
#     # this happens when the server is killed. (i.e kill process from terminal )
#     # or there is a non recoverable exception, and the server process is killed internally
#     server.close()
# This port range is considered safe to use by IANA
class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        # Get port socket or something? If fail, exit...
    # 
    @staticmethod
    def start():
        print("Server Info")
        (ip, port) = helpers.getIpAndPortFromUser()
        print(ip, port)
        try:
            return Server(ip, port)
        except Exception:
            print("Error creating server with ip: {} port: {}".format(ip, port))
    # Main server logic
    def run():
        pass

if __name__=='__main__':
    Server.start()