# -*- coding: utf-8 -*-
""" The peer """
import json

# local imports
from server import Server
from client import Client
from logger import Logging
from resource import Resource
from message import Message
from swarm import Swarm
import queue
import time
import threading

logger = Logging()

class Peer(Server):

    # status
    PEER = 0
    SEEDER = 1
    LEECHER = 2
    BITFIELD_LOCK = threading.Lock()
    MESSAGE_QUEUE_LOCK = threading.Lock()

    def __init__(self, max_upload_rate = None, max_download_rate = None, is_seed=False):
        """
        TODO: implement the class constructor
        """
        Server.__init__(self, '127.0.0.1') # inherits methods from Server class, temporary inputs for ip
        # Client.__init__(self) # inherits methods from Client class
        self.status = self.PEER if not is_seed else self.SEEDER
        self.chocked = 0
        self.interested = 0
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
        # Queue used to hold messages for main message thread to handle
        self.tracker_message_queue = queue.Queue()

    def start(self, torrent_path):
        """
        Entry point for peer to peer/tracker interactions
        """
        self.resource = self.get_metainfo(torrent_path, self.status == self.SEEDER)

        tracker = self.resource.get_trackers()[0]

        self.swarm = self.connect_to_tracker(tracker.split(":")[0], tracker.split(":")[1], self.resource.name())

        self.connect_to_swarm(self.swarm)

        self.listen(self.handle_client) # ' become a server.'

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

        # start new thread to constantly poll tracker for new connections and connecting them?
        threading.Thread(target=self.handle_tracker_swarm_updates, args=()).start()
        # start new thread to send message to tracker
        threading.Thread(target=self.handle_tracker_messaging, args=()).start()
        
        return res

    def handle_tracker_messaging(self):
        """
        Singleton thread that sends message over self.tracker_clients 
        """
        while True:
            try:
                with self.MESSAGE_QUEUE_LOCK:
                    # grabs message from queue
                    message = self.tracker_message_queue.get(block=False)
                self.tracker_client.send(message)

                res = self.tracker_client.receive()

                if isinstance(res, Swarm): # if was a 'get_swarm' call, 
                    self.swarm = res
                    for new_peer in self.swarm.peers:
                        is_new = True
                        for peer in self.peer_clients:
                            # if already in peers list, update status
                            if peer[0][2] == new_peer[2]: # if peer_ids match
                                # update peer's status
                                peer[0][3] = new_peer[3]
                                is_new = False
                                break
                        # # if peer is new and not me
                        if is_new and new_peer[2] != self.peer_id:
                            # create new connection w/ peer and add to peer_clients.
                            self._connect_to_peer(new_peer)
            except queue.Empty:
                # if queue is empty, wait
                time.sleep(0.50)

    def handle_tracker_swarm_updates(self):
        """
        This thread handles polling the tracker every 15 seconds for new updates to the swarm
        Function then creates connection to the new peers.
        It also updates the peer statuses in the peer's list of peer_clients
        """
        while self.status != self.SEEDER:
            time.sleep(3)
            # ask tracker for swarm object
            with self.MESSAGE_QUEUE_LOCK:
                self.tracker_message_queue.put({"option": "get_swarm", "message": self.resource.name()})

    def _connect_to_peer(self, peer):
        print(f"Connecting to Peer_id: {peer[2]}")
        # connect to peer
        client = Client()
        client.connect(peer[0], peer[1])
        # adds peer info and connection socket 
        self.peer_clients.append([peer, client])
        # employ a new thread to talk to each peer...
        thread_c = threading.Thread(target=self.handle_peer, args=(client, peer))
        thread_c.start()

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
        self.interested = 1
        for peer in swarm.peers:
            if peer[2] != self.peer_id: # if not me
                self._connect_to_peer(peer)

    def handle_client(self, client_sock, client_addr):
        """
        Function to handle client connections
        """
        while True:
            req = self.receive(client_sock)
            message = Message()
            message.chocked = self.chocked
            message.bitfield = self.resource.completed
            if req.interested != 1:
                self.send(client_sock,message)
                if req.keep_alive != 1: 
                    break
                continue
            #
            if req.request is None:
                # must have set the cancel field instead.
                # will be last message, set keep_alive to 0
                message.keep_alive = 1
                requested_piece_index = req.cancel["index"]
                requested_block_index = req.cancel["block_id"]
            else:
                requested_piece_index = req.request["index"]
                requested_block_index = req.request["block_id"]
            # NOTE: THIS IS ASSUMING THAT SENDER ASKED FOR SOMETHING I HAVE
            piece = self.resource.get_piece(requested_piece_index)
            block = piece.blocks[requested_block_index]

            message.piece["index"] = requested_piece_index
            message.piece["block_id"] = requested_block_index
            message.piece["block"] = block.data
            print(f"Sending Piece: {requested_piece_index} Block: {requested_block_index} to IP {client_addr[0]}")
            self.send(client_sock,message)

    def handle_peer(self, client, peer):
        """
        Threaded function to handle connection to peer, note this connection
        is only useful if self is not a seeder
        """
        # send initial info
        message = Message()
        message.interested = self.interested
        message.bitfield = self.resource.completed
        message.keep_alive = 1
        client.send(message)

        # while peer is not a seeder
        while self.status != self.SEEDER:
            res = client.receive() #.receive()
            # see what they have
            if res.chocked == 1:
                # if chock, wait a bit, then send message again
                time.sleep(2)
                client.send(message)
                continue; # go back to the start
            # if not chocked!
            for i in range(len(res.bitfield)):
                if res.bitfield[i] == 1 and self.resource.completed[i] == 0:
                    # if he has and I don't
                    self._get_piece(client, peer, i)
            
            # check if have everything
            done = True
            print("Completed: ", self.resource.completed)
            for i in range(len(self.resource.completed)):
                if self.resource.completed[i] != 1:
                    done = False
                    break
            if done:
                self.change_role(self.SEEDER)
                self.resource.save_torrent()
                break;

    def _get_piece(self, client, peer, index):
        with self.BITFIELD_LOCK: # make sure piece is not being satisfied
            if self.resource.completed[index] != 0:
                return ;
            else:
                self.resource.completed[index] = 0.5
        piece = self.resource.get_piece(index)
        # for each piece in block
        for i in range(len(piece.blocks)):
            # send request
            message = Message()
            message.interested = 1
            message.keep_alive = 1
            message.bitfield = self.resource.completed
            if i == len(piece.blocks) - 1: # if last block
                message.request = None
                message.cancel["index"] = index
                message.cancel["block_id"] = i
            else:
                message.request["index"] = index
                message.request["block_id"] = i
            client.send(message)
            # get response
            res = client.receive() #.receive()
            piece.blocks[i].fill_data(res.piece["block"])
            print(f"Got Piece: {index} Block: {i}")
        # when done, set completed to 1

        # See if hash matches 
        if not piece.set_to_complete(self.resource.get_piece_hash(index)):
            # if not
            with self.BITFIELD_LOCK: # make sure piece is not being satisfied
                self.resource.completed[index] = 0
            return False
        with self.BITFIELD_LOCK:
            self.resource.completed[index] = 1
        return True

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
        ma_map = Resource.parse_metainfo(torrent_path)

        resource = Resource(resource_id=ma_map["file_name"],file_path=ma_map["path"],file_len=ma_map["file_len"], piece_len=ma_map["piece_len"], pieces_hash=ma_map["pieces"], seed = seeder)

        resource.add_tracker(ma_map["tracker_ip_address"], ma_map["tracker_port"])

        return resource

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
        self.status = new_role
        name = ""
        if new_role == self.SEEDER:
            name = "SEEDER"
        elif new_role == self.LEECHER:
            name = "LEECHER"
        else:
            name = "PEER"
        print("Status:", name)
        with self.MESSAGE_QUEUE_LOCK:
            self.tracker_message_queue.put({"option": "change_peer_status", "message": {
            "peer":[self.host_ip, self.host_port, self.peer_id, self.status],  # key identifying features for peer
            "resource_id": self.resource.name()
        }})

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
