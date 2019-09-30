"""

This module contains helper functions used in tcp-message-app.

"""
import re

# these ports are suggested by IANA
MIN_IANA_PORT = 49152
MAX_IANA_PORT = 65535

MAX_NUM_CONNECTIONS = 5
BUFFER_SIZE = 4096

TEST_PORT = 50000

def getIpFromUser(custom_prompt="IP Address: "):
    while True:
        ip = input(custom_prompt)
        is_ip = re.search(r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$',ip)
        if is_ip:
            break
    return ip;

def getPortFromUser(custom_prompt="port listening:"):
    custom_prompt += "({}-{}) ".format(MIN_IANA_PORT, MAX_IANA_PORT)
    while True:
        port = int(input(custom_prompt))
        if MIN_IANA_PORT <= port <= MAX_IANA_PORT:
            break
    return port

class DisconnectSignal(Exception):
    """Exception to denote a safe disconnect request"""
    pass

class ClientDisconnect(DisconnectSignal):
    """Exception to denote a client disconnecting from server"""
    pass

class ServerDisconnect(DisconnectSignal):
    """Exception to denote a server disconnecting from client"""
    pass