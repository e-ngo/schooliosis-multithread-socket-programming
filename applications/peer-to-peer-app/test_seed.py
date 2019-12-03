import json
from peer import Peer

"""
Script aims to provide execution flow of objects...

"""
if __name__ == "__main__":
    peer = Peer(5,5)
    resource = peer.get_metainfo("./random_jpeg_seed.torrent", True)

    tracker = resource.get_trackers()[0]

    swarm = peer.connect_to_tracker(tracker.split(":")[0], tracker.split(":")[1], resource.name())
    
    resource.save_torrent("./test_save.jpeg")
    
    print(swarm.peers)