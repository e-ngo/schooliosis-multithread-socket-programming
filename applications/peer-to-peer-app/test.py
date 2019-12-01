import json
from peer import Peer

"""
Script aims to provide execution flow of objects...

"""
if __name__ == "__main__":
    peer = Peer(5,5)
    meta_info = peer.get_metainfo("./random_jpeg.torrent")
        
    # for key in json_data.keys():
    #     print(key)
    print(meta_info["info"]["length"])
    print(dir(peer))
    # extract tracker information
    temp = meta_info["announce"].split(":")
    if len(temp) < 2 or len(temp) > 3:
        exit(1)

    tracker_port = temp[-1]
    tracker_url = temp[-2]
   
    tracker_ip = tracker_url.split("//")[-1]

    resource_name = meta_info["info"]["name"]
    torrent_length = meta_info["info"]["length"]
    piece_length = meta_info["info"]["piece length"]
    pieces = meta_info["info"]["pieces"]
    print(tracker_ip, tracker_port, resource_name)

    swarm = peer.connect_to_tracker(tracker_ip, tracker_port, resource_name)
    print(swarm)