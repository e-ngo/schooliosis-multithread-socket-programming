import json
from peer import Peer

"""
Script aims to provide execution flow of seeder...

"""
if __name__ == "__main__":
    peer = Peer(5,5, is_seed = True)

    peer.start()
    
    peer.resource.save_torrent("./test_save.jpeg")
    
    print(peer.swarm.peers)