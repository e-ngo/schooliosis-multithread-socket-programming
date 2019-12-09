# -*- coding: utf-8 -*-
""" The tracker
This file implements the Tracker class. The tracker has two main functionalities
 (1) A client connects to a tracker, and a tracker sends
all the peers ip addresses and ports connected to the swarm that are sharing
the same resource. Since a tracker can handle more than one swarm, then the
swarm needs to be identified with a id (i.e the file id that is being shared
in the swarm)
 (2) When a peers change status (become leechers or seeders) they must inform
 the tracker, so the tracker can update that info in the swarm where they are
 sharing the resource

Centralized server, holds infor about one or more torresntand associated swarms.
Functions as gateway for peers into a swarm. 
In centralized P2P, functions as HTTP service and does not provide accesds to any downlaoding data.
"""
from swarm import Swarm
from resource import Resource
from server import Server

import pickle
import threading

class Tracker(Server):

    PORT = 50000
    IP_ADDRESS = "127.0.0.1"
    SWARM_LOCK = threading.Lock()
    MAX_PEERS = 10

    def __init__(self, ip_address = None, port = 0, file_path = None):
        """
        TODO: finish constructor implementation (if needed)
        If parameters ip_address and port are not set at the object creation time,
        you need to use the default IP address and the default port set in the class constants.
        :param ip_address:
        :param port:
        """
        self.IP_ADDRESS = ip_address or self.IP_ADDRESS
        self.PORT = port or self.PORT
        Server.__init__(self,  self.IP_ADDRESS, self.PORT)
        # the list of swarms that this tracker keeps
        if file_path:
            self.swarms = self.current_swarms_or_new(file_path)
        else: 
            self.swarms = self.current_swarms_or_new()
        print("Current swarms list: ", self.swarms)

    def current_swarms_or_new(self, file_path = "./tmp/swarms.pickle"):
        """
        Attempts to pull the old swarms list from storage
        """
        try:
            with open(file_path, "rb") as file_handle:
                s = pickle.load(file_handle)
        except FileNotFoundError:
            s = []
        finally:
            return s or []


    def handle_client_logic(self, client_sock, client_addr):
        """
        This function contains the logic that will go into the server's main client handling logic.
        """
        # on intiial connection send new client their peer_id (process id).
        self.send(client_sock, client_addr[1])

        # main server loop
        while True: # Should this be a loop? 
            request = self.receive(client_sock) # {"option", "message"}
            option = request["option"]
            data = request["message"]

            if option == "get_swarm":
                self.send_peers(client_sock, data)
                continue
            # elif option == "get_peer":
            #     # self.get_
            #     pass #TODO?
            elif option == "add_peer_to_swarm":
                res = self.add_peer_to_swarm(data["peer"], data["resource_id"])
            # elif option == "change_peer_status":
            #     res = self.change_peer_status(data["peer"], data["resource_id"])
            # elif option == "add_swarm":
            #     res = self.add_swarm(data)
            # elif option == "remove_swarm":
            #     res = self.remove_swarm(data)
            else:
                print("Invalid option")
                break
            self.send(client_sock, res)

    def add_swarm(self, swarm):
        """
        Already implemented
        Add a Swarm object to the swarms list of the tracker
        :param swarm:
        :return:
        """
        self.swarms.append(swarm)
        return True

    def remove_swarm(self, resource_id):
        """
        TODO: implement this method
        Given a resource id, remove the swarm from the tracker
        that is sharing this resource id.
        This happens normally when there is no seeder sharing
        this resource.
        :param resource_id:
        :return: VOID
        """
        for swarm in self.swarms:
            if swarm.resource_id == resource_id:
                del swarm
                self.make_persistent()
                return True
        return False

    def peer_in_swarm(self, peer, swarm):
        """
        Returns if peer already in swarm
        """
        for pere in swarm.peers:
            if peer[0] == pere[0] and peer[1] == pere[1]:
                # update status if applicable...
                pere[2] = peer[2]
                return True
            return False

    def add_peer_to_swarm(self, peer, resource_id, swarm = None):
        """
        TODO: implement this method
        Based on the resource_id provided, iterate over the
        swarms list, and when resource_id matchs, add the
        new peer to the swarm.
        :param peer: (peer_ip, peer_port)
        :param resource_id:
        :return: VOID
        """
        print(f"Adding peer to {resource_id} swarm")
        swarm = swarm or self._get_swarm_object(resource_id)

        if not swarm:
            swarm = Swarm(resource_id)
            self.add_swarm(swarm)
            
        print(peer)
        print(swarm)
        # avoid dups
        if not self.peer_in_swarm(peer, swarm):
            swarm.add_peer(peer)
        self.make_persistent()
        return True
        # return False # error

    def _get_swarm_object(self, resource_id):
        """
        Given resource_id, returns swarm object in swarms list 
        that has resource_id
        :param resource_id:
        :return swarm_object:
        """
        ret = None
        for swarm in self.swarms:
            if swarm.resource_id == resource_id:
                ret = swarm
                break
        return ret

    def change_peer_status(self, peer, resource_id):
        """
        TODO: implement this method
        When a peers in a swarm report a change of status
        (leecher or seeder) then, get the swarm object from
        the swarm list, and update the status in the swarm of
        such peer.
        :param resource_id:
        :return: VOID
        """
        swarm = self._get_swarm_object(resource_id) # TODO

        # if swarm:
        #     swarm.(peer)
        #     return True
        # return False
        # ???
        self.make_persistent()
        return False

    def send_peers(self, peer_socket, resource_id):
        """
        TODO: implement this method
        Iterate the swarms list, and find the one which match with
        the resource id provided as a parameter. Then, serialize the
        swarm and send the swarm object to the peer requesting it.
        :param peer_socket: the peer socket that is requesting the info
        :param resource_id: the resource id to identify the swarm
               sharing this resource
        :return: VOID
        """
        print(f"Sending {resource_id} swarm information")
        swarm = self._get_swarm_object(resource_id)
        # if swarm DNE, create it
        # if not swarm:
        #     swarm = Swarm(resource_id)
        #     self.add_swarm(swarm)
        # self.add_peer_to_swarm((), resource_id, swarm)
        print(swarm)
        self.send(peer_socket, swarm)

    def make_persistent(self, file_path="./tmp/swarms.pickle"):
        """
        Given a set ???
        """
        with self.SWARM_LOCK:
            with open(file_path, "wb") as file_handle:
                pickle.dump(self.swarms, file_handle, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    tracker = Tracker()
    print(tracker.host_ip)
    print(tracker.host_port)
    tracker.listen(tracker.handle_client_logic)
