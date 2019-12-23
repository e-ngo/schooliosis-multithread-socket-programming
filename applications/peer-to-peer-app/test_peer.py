import json
from peer import Peer

"""
Script aims to provide execution flow of leecher...

"""
if __name__ == "__main__":
    peer = Peer(5,5)

    path = input('Path to torrent file: ')

    peer.start(path)