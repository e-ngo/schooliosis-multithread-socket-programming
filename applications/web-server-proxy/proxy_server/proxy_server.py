import os,sys,threading,socket
from proxy_thread import ProxyThread
import urllib

class ProxyServer:

    HOST = '127.0.0.1'
    PORT = 12001
    BACKLOG = 50
    MAX_DATA_RECV = 4096

    def __init__(self):
        self.clients = {}

    def run(self):
        try:
            # create a socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # associate the socket to host and port
            server_socket.bind((self.HOST, self.PORT))
            # listen and accept clients
            server_socket.listen(self.BACKLOG)
            print(f"Server started\nListening at {self.HOST}({self.PORT}):")
            while True:
                self.accept_clients(server_socket)
            
        except socket.error as sock_error:
            print(sock_error)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print("An exception has occurred", e)

        server_socket.close()
        print("Closing the proxy server")
        os._exit(0)

    def accept_clients(self, server_socket):
        """
        Accept clients that try to connect. 
       :return: 
        """
        client_sock, addr = server_socket.accept()
        # self.clients[addr[1]] = client_sock
        print(f"Client {addr} has connected!")
        thread = threading.Thread(target=self.proxy_thread, args=(client_sock, addr))
        thread.start()

    def proxy_thread(self, conn, client_addr):
        """
        I made this method for you. It is already completed and no need to modify it. 
        This already creates the threads for the proxy is up to you to find out where to put it.
        Hint: since we are using non-persistent connections. Then, when a clients connects, 
        it also means that it already has a request to be made. Think about the difference 
        between this and assign#1 when you created a new thread. 
        :param conn: 
        :param client_addr: 
        :return: 
        """
        print("Thread {} started".format(client_addr[1]))
        proxy_thread = ProxyThread(conn, client_addr, self.HOST)
        proxy_thread.init_thread()
        # del self.clients[client_addr[1]]
        print("Thread {} ended".format(client_addr[1]))

if __name__=="__main__":
    server = ProxyServer()
    server.run()