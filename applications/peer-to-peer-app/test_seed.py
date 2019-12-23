import json
from peer import Peer

"""
Script aims to provide execution flow of seeder...

"""
if __name__ == "__main__":
    peer = Peer(5,5, is_seed = True)

    print("Starting p2p as SEED")

    path = input('Path to torrent file: ')

    peer.start(path)