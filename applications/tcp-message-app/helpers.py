"""

This module contains helper functions used in tcp-message-app.

"""
import re

# these ports are suggested by IANA
MIN_IANA_PORT = 49152
MAX_IANA_PORT = 65535

def getIpAndPortFromUser():
    while True:
        ip = raw_input("IP Address: ")
        is_ip = re.search(r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$',ip)
        if is_ip:
            break
    while True:
        port = int(raw_input("port listening:({}-{}) ".format(MIN_IANA_PORT, MAX_IANA_PORT)))
        if MIN_IANA_PORT <= port <= MAX_IANA_PORT:
            break
    return (ip, port)