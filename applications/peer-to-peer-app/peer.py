# -*- coding: utf-8 -*-
""" The peer """
import json

# local imports
from server import Server
from client import Client
from logger import Logging
from resource import Resource

logger = Logging()

"""
TODO:
Queue for reading
Queue for writing
1 threads to read and decide what to do, another for writing to every client.
1 for server loop
x threads for client connection to server
x threads for peer connection to server
"""

class Peer(Client, Server):

    # status
    PEER = 0
    SEEDER = 1
    LEECHER = 2

    def __init__(self, max_upload_rate = None, max_download_rate = None, is_seed=False):
        """
        TODO: implement the class constructor
        """
        Server.__init__(self, '127.0.0.1') # inherites methods from Server class, temporary inputs for ip
        Client.__init__(self) # inherites methods from Client class
        self.status = self.PEER if not is_seed else self.SEEDER
        self.chocked = False
        self.interested = False
        if max_download_rate:
            self.max_download_rate = max_download_rate
        else:
            self.max_download_rate = int(input("Input Max Download Rate (b/s): "))
        if max_upload_rate:
            self.max_upload_rate = max_upload_rate
        else:
            self.max_upload_rate = int(input("Input Max Upload Rate (b/s): "))
        self.peer_id = None
        self.tracker_client = None
        self.peer_clients = []

        self.resource = None
        self.swarm = None

    def start(self, torrent_path):
        """
        Entry point for peer to peer/tracker interactions
        """
        self.resource = self.get_metainfo(torrent_path, self.status == self.SEEDER)

        tracker = self.resource.get_trackers()[0]

        self.swarm = self.connect_to_tracker(tracker.split(":")[0], tracker.split(":")[1], self.resource.name())

        self.connect_to_swarm(self.swarm)

    def connect_to_tracker(self, ip_address, port, resource_name):
        """
        TODO: implement this method
        Connect to the tracker. Note that a tracker in this assignment
        is similar to the server in assignment #1. So, you already know
        how to implement this connection
        Note that ip address and port comes from the announce in
        the torrent file. So you need to parse it firt at some point
        :param ip_address:
        :param port:
        :return: the swarm object with all the info from the peers connected to the swarm
        """
        self.tracker_client = Client()

        self.tracker_client.connect(ip_address, port)
        # get peer_id
        self.peer_id = self.tracker_client.receive()

        # add self to list of clients... this is done in tracker?...
        self.tracker_client.send({"option": "add_peer_to_swarm", "message": {
            "peer":[self.host_ip, self.host_port, self.peer_id, self.status],  # key identifying features for peer
            "resource_id": resource_name
        }})

        tmp = self.tracker_client.receive()

        if not tmp:
            raise Exception("Could not add peer to swarm")

        self.tracker_client.send({"option": "get_swarm", "message": resource_name})
        # MRO pulls from client because invalid function signature for server
        
        res = self.tracker_client.receive()
        
        return res

    def connect_to_swarm(self, swarm):
        """
        TODO: implement this method
        This method will create a socket (TCP) connection
        with all the peers in the swarm sharing the requested
        resource.
        Take into consideration that even if you are connected
        to the swarm. You do not become a leecher until you set
        your status to interested, and at least one of the leechers
        or seeders in the swarm is not chocked.
        :param swarm: Swarm object returned from the tracker
        :return: VOID
        """
        for peer in swarm.peers:
            #TODO Wrap in try catch
            if peer[2] != self.peer_id: # if not me
                print(f"Connecting to {peer}")
                # connect to peer
                client = Client()
                client.connect(peer[0], peer[1])
                # adds peer info and connection socket 
                self.peer_clients.append(peer, client)
                # start new thread?....
        

    def upload_rate(self):
        """
        TODO: implement this method
        Compute the actual upload rate using the formule from assignment docs
        This needs to be re-evaluated every 30 seconds approximatly
        :return: the new upload_rate
        """
        return None

    def download_rate(self):
        """
        TODO: implement this method
        Compute the actual download rate using the formule from assignment docs
        This needs to be re-evaluated every 30 seconds approximatly
        :return: the new download rate
        """
        return None


    def get_metainfo(self, torrent_path, seeder = False):
        """
        (1) Create an empty resource object
        (2) call the method parse_metainfo() from that object
            which must return all the fields and values from
            the metainfo file, including the hashes from the
            file pieces.
        :param torrent_path:
        :return: the metainfo
        """
        # should resource_id be a random number?...
        # try:
        ma_map = Resource.parse_metainfo(torrent_path)

        resource = Resource(resource_id=ma_map["file_name"],file_path=ma_map["path"],file_len=ma_map["file_len"], piece_len=ma_map["piece_len"], pieces_hash=ma_map["pieces"], seed = seeder)

        resource.add_tracker(ma_map["tracker_ip_address"], ma_map["tracker_port"])

        return resource

        # except FileNotFoundError:
        #     print(f"File: {torrent_path} not found")
        # except Exception as e:
        #     print(e)
        # logger.log("Peer", "Something went wrong getting metainfo")
        
        # raise Exception(f"Error getting metainfo from {torrent_path}")

    def change_role(self, new_role):
        """
        TODO: implement this method
        When a peer is interested in downloading a pieces of
        a resource, and the seeder or leecher sharing the resource
        is not chocked, then the peer becomes a leecher. When the
        leecher already have all the completed files from the file
        it becomes a seeder.
        :param new_role: use class constants: PEER, SEEDER or LEECHER
        :return: VOID
        """
        pass

    def send_message(self, block, start_index = -1, end_index = -1):
        """
        TODO: implement this method
        (1) Create a message object from the message class
        (2) Set all the properties of the message object
        (3) If the start index and end_index are not negative
            then, that means that the block needs to be sent
            in parts. implement that situations too.
        (4) Don't forget to check for exceptions with try-catch
            before sending messages. Also, don't forget to
            serialize the message object before being sent
        :param block: a block object from the Block class
        :param start_index: the start index (if any) of the data being sent
        :param end_index: the end index of the data being sent
        :return: VOID
        """
        pass

    def receive_message(self):
        """
        TODO: implement this method
        (1) receive the message
        (2) inspect the message (i.e does it have payload)
        (4) If this was the last block of a piece, then you need
            to compare the piece with the sha1 from the torrent file
            if is the same hash, then you have a complete piece. So, set
            the piece object related to that piece to completed.
        (5) Save the piece data in the downloads file.
        (6) Start sharing the piece with other peers.
        :return: VOID
        """
        pass

    def get_top_four_peers(self):
        """
        TODO: implement this method
        Since we are implementing the 'tit-for-tat' algorithm
        which upload data to the top 4 peers in the swarm (max rate upload peers)
        then this method will inspect the swarm object returned by the tracker
        and will get the 4 top peers with highest upload rates. This method needs to
        be re-evaluated every 30 seconds.
        :return: a list of the 4 top peers in the swarm
        """
        self.top_four = []
        # your implementation here
        return self.top_four

    def verify_piece_downloaded(self, piece):
        """
        TODO: implement this method
        :param piece: the piece object of this piece
        :return: true if the piece is verified and is not corrupted, otherwisem, return false
        """
        return False

    def is_chocked(self):
        """
        Already implemented
        :return:
        """
        return self.chocked

    def is_interested(self):
        """
        Already implemented
        :return:
        """
        return self.interested

    def chocked(self):
        """
        Already implemented
        :return: VOID
        """
        self.chocked = True

    def unchocked(self):
        """
        Already implemented
        :return: VOID
        """
        self.chocked = False

    def interested(self):
        """
        Already implemented
        :return: VOID
        """
        self.interested = True

    def not_interested(self):
        """

        Already implemented
        :return: VOID
        """
        self.interested = False

