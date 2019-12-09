import json
from peer import Peer

"""
Script aims to provide execution flow of leecher...

"""
if __name__ == "__main__":
    peer = Peer(5,5)
    resource = peer.get_metainfo("./random_pdf.torrent")

    tracker = resource.get_trackers()[0]

    swarm = peer.connect_to_tracker(tracker.split(":")[0], tracker.split(":")[1], resource.name())
    


    print(swarm.peers)