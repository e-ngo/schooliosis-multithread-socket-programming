import os,sys,thread,socket
from proxy_thread import ProxyThread

class ProxyServer(object):

    HOST = '127.0.0.1'
    PORT = 12000
    BACKLOG = 50
    MAX_DATA_RECV = 4096

    def __init__(self):
        self.clients = []

    def run(self):
        try:
            # create a socket
            # associate the socket to host and port
            # listen and accept clients
            print("Dummy print statement to avoid complile errors in the template. Remove it later")
        except socket.error, (value, message):
            print(message)


    def accept_clients(self):
        """
        Accept clients that try to connect. 
       :return: 
        """
        return 0



    def proxy_thread(self, conn, client_addr):
        """
        I made this method for you. It is already completed and no need to modify it. 
        This already creates the threads for the proxy is up to you to find out where to put it.
        Hint: since we are using only  non-persistent connections. Then, when a clients connects, 
        it also means that it already has a request to be made. Think about the difference 
        between this and assign#1 when you created a new thread. 
        :param conn: 
        :param client_addr: 
        :return: 
        """
        proxy_thread = ProxyThread(conn, client_addr)
        proxy_thread.init_thread()


server = ProxyServer()
server.run()