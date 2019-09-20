"""

a.) TCP Client in charge of
1.) Connect to server
2.) Send requests to the server
3.) Retrieve responses from the server.
Retrieved responses from the server are handeld by TCPClientHandler, 
    which is the worker class that provides all the menu actions executed from client size.
b.) after executing client.py script, should show a menu where user can select different actions.
c.) Options

"""
import helpers


if __name__ == '__main__':
    (ip, port) = helpers.getIpAndPortFromUser()