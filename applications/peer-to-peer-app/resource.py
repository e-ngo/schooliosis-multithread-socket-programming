# -*- coding: utf-8 -*-
""" The Resource, Piece and Block classes
This file contains the classes Resource, Piece and Block to provide
services and functionalities needed from a resource in a swarm.
"""
import hashlib
import json
import math
from bitstring import BitArray, BitStream

def remove_tags(string):
    """
    Given string, removes any bracket tags, ie. "<hex>f" => "f"
    """
    starter = -1
    for i in range(len(string)): # look for the start of tag?
        if string[i] == "<":
            starter = i
            break
    if starter == -1:
        return string #nothing to remove here
    
    ender = -1
    for i in range(starter, len(string)):
        if string[i] == ">":
            ender = i
            break
    if ender == -1:
        return string # nothing to remove here...

    return string[0: starter] + string[ender: ]

class Resource(object):
    """
    This class provides services to handle resources
    """
    def __init__(self, resource_id = 0, file_path = None, file_len = 0, piece_len = 0, pieces_hash = None, seed = False):#, file_name = None ):
        """
        TODO: complete the implementation of this constructor.
        :param resource_id: default 0
        :param file_path: default None
        :param file_len: default 0
        :param piece_len: default 0
        """
        self.file_path = file_path # for non seeds, this is install path. For seeds, this is file path
        self.resource_id = resource_id # file name is resource_id
        self.len = file_len
        self.max_piece_size = piece_len
        self.trackers = []
        self.completed = []  # the pieces that are already completed
        # self.file_name = file_name
        self.seed = seed
        self.expected_pieces_hash = self.parse_hex_string_to_array(pieces_hash)
        self._create_pieces() # creates the file's pieces

    def parse_hex_string_to_array(self, hex_string, delimiter = " "):
        """
        Given hex string with space delimiters
        """
        if not isinstance(hex_string, str):
            return hex_string
        # assuming in format: <hex>ff ff ff ff</hex> (note the space delimiters.)
        hashes = hex_string.split(delimiter)
        hashes[0] = remove_tags(hashes[0])
        hashes[-1] = remove_tags(hashes[-1])

        return hashes


    def add_tracker(self, ip_address, port):
        """
        TODO: Implement this method
        (1) Create the announce ip_address:port (i,e '127.0.0.1:12000')
        (2) Add the announce to the trackers list.
        :param ip_address:
        :param port:
        :return: VOID
        """
        self.trackers.append(f"{ip_address}:{port}")

    def get_trackers(self):
        """
        Already implemented
        :return: the list of trackers for this resource
        """
        return self.trackers

    def len(self):
        """
        Already implementeted
        :return: the len of the resource
        """
        return self.len

    def name(self):
        """
        Extract the name of the file path from the path
        :return: the name of the file
        """
        # return self.file_name or self.file_path.split("/")[-1]
        return self.resource_id # I am using resource_id to hold name

    def _create_pieces(self):
        """
        Private method.
        This method will divide the file in pieces (same size)
        with the only exception of the last piece which has
        the left over bytes.
        :return: VOID
        """
        self.pieces = [] # list of objects of pieces. (see Piece class)
        # hash groupings (160 bits for sha1 hash), about 20 hexadecimal chars
        num_pieces = math.ceil(self.len / self.max_piece_size)

        if self.seed: # if not seed, data will be None
            with open(self.file_path, "rb") as seed_file:
                for i in range(num_pieces):
                    chunk = seed_file.read(self.max_piece_size)
                    self.pieces.append(Piece(chunk, i, self.resource_id, self.max_piece_size, self.seed))
                    self.completed.append(1)
        else:
            for i in range(num_pieces):
                self.pieces.append(Piece(None, i, self.resource_id, self.max_piece_size))
                self.completed.append(0)

    def get_piece(self, index):
        """
        Already Implemented
        :param piece_id:
        :return: the piece requested
        """
        return self.pieces[index]

    def sha1_hashes(self):
        """
        TODO: implement this method.
        In this method you need to return all the
        sha1 hashes from each piece of the file
        1. iterate over the pieces list
        2. For each piece get its sh1a hash
        3. Add that hash to the hashes list below
        4. return the hashes list
        """
        hashes = []
        # assuming files are in the format
        for piece in self.pieces:
            hashes.append(piece.get_hash)

        return hashes

    @staticmethod
    def parse_metainfo(file_path):
        """
        TODO: implement this method
        Parse the ,torrent file containing the metainfo for this resource
        and save all the info in instances variables of this class so the
        metainfo of the torrent can be easily accessible by the peer.
        :param file_path: the path to the metainfo (extension torrent)
                          file to be parsed
        :return: a python dictionary with the following keys:
                 (file_name, tracker_ip_address, tracker_port, piece_len, file_len, pieces}
                 Note that the key pieces will store the list of sh1a hashes from each piece
                 of the file. You can assume
        """
        with open(file_path, "r") as file_handle:
            json_data = json.load(file_handle)

        temp = json_data["announce"].split(":")
        if len(temp) < 2 or len(temp) > 3:
            raise Exception("Torrent tracker announce has invalid format")

        tracker_port = temp[-1]
        tracker_url = temp[-2]

        tracker_ip = tracker_url.split("//")[-1]

        resource_path = json_data["info"]["path"] # for peers, is the install path. for seeds, this is the file_path
        resource_id = json_data["info"]["name"]

        torrent_length = json_data["info"]["length"]
        piece_length = json_data["info"]["piece length"]
        pieces = json_data["info"]["pieces"]

        return {"file_name":resource_id, "tracker_ip_address":tracker_ip, "tracker_port":tracker_port, "piece_len":piece_length, "file_len": torrent_length, "pieces":pieces, "path": resource_path}

    def save_torrent(self, file_path = None):
        """
        After all data sent, all hashes checked, save file to storage to given file_path
        """
        file_path = file_path or self.file_path # should be self.file_path
        once = False
        with open(file_path , "wb") as fw:
            for piece in self.pieces:
                for block in piece.blocks:
                    # print(block.piece_id, block.block_id, block.data)
                    if not once:
                        print(f"Piece num {len(self.pieces)} block num {len(piece.blocks)} Total size {self.len}")
                        once = True
                    fw.write(block.data)

class Piece(object):
    """
    This class provides the services needed to handle pieces from a resource (file)
    """
    BLOCK_SIZE = 1024
    def __init__(self, data, piece_id, resource_id, max_piece_size, seed = False, override_block_size = None):
        self.data = data
        self.resource_id = resource_id
        self.piece_id = piece_id
        self.completed = False
        self.max_piece_size = max_piece_size
        self.seed = seed
        self.block_size = override_block_size if override_block_size else self.BLOCK_SIZE
        self._create_blocks(self.block_size)
        self.hash = self._set_hash_sha1()

    def _create_blocks(self, max_size_in_bytes = 1024):
        """
        TODO: implement this method
        (1) It is important here to create small chucks of data
            (block) that can be shared without compromising the
            app performance. A max size of 16KB is recomended
        (2) Convert the max_size to bytes (max_size * 1024)
        (3) Divide the piece in blocks of the same size. For example,
            a piece should have 256 blocks or more each one of 16KB
        (4) Append blocks created to the blocks list below
        (5) Return the blocks
        :param max_size: 16 KB set by default
    :return: the blocks
        """
        self.blocks = []

        block_len = math.ceil(self.max_piece_size / max_size_in_bytes)

        for i in range(block_len):
            print(f"MPS: {self.max_piece_size}, MSIB: {max_size_in_bytes}")
            block = Block(i, self.piece_id, self.resource_id)
            if self.data:
                start = i * max_size_in_bytes
                end = min((i + 1) * max_size_in_bytes , self.max_piece_size)
                data = self.data[start:end]
                print(f"Start: {start}, End: {end}")
                print(f"Data: {data}")
                block.fill_data(data)
            self.blocks.append(block)
        return self.blocks

    def _set_hash_sha1(self, data = None):
        """
        Already implemented for you.
        Takes a string data, and create a sha1 hash
        you need to put this hash in the torrent file
        so, when a piece is downloaded, then hash of
        that piece needs to be compared in irder to
        make sure that the data is not corrupted.
        :return: the hexadecimal representation of
        the hash
        """
        if not data:
            data = self.data
        if not data:
            return None
        if isinstance(data, str):
            data = data.encode() # 
        hash_object = hashlib.sha1(data)
        return hash_object.hexdigest()

    def get_hash(self):
        """
        Already implemented
        :return: the hash of this piece
        """
        return self.hash

    def is_equal_to(self, piece):
        """
        TODO: implement this method
        Check if two pieces are the same.
        Note that you need to check their sha1 hashes
        to confirm that they are the same piece. For example,
        if you completed the download of a piece from another peer,
        you'll need to check the sha1 hash of that piece against the
        all the sha1 of all the pieces in the .torrent file.
        If there is a match, then if the piece is not corrupted,
        and the piece is now complete. Otherwise, the peer will need
        to request the piece of the file again.
        :param piece: another piece
        :return:
        """
        return False

    def get_blocks(self):
        """
        Already implemented
        :return:
        """
        return self.blocks

    def is_completed(self):
        """
        Already implemented
        :return:
        """
        return self.completed

    def set_to_complete(self):
        """
        Already implemented
        :return:
        """
        self.completed = True


class Block(object):
    """
    This class implements all the services provided by a block from piece
    """
    def __init__(self, block_id, piece_id, resource_id):
        self.resource_id = resource_id
        self.piece_id = piece_id
        self.block_id = block_id
        self.data = None

    def fill_data(self, data):
        """
        Setter for data
        
        """
        self.data = data

    def get_data(self):
        """
        Getter for data 
        """
        return self.data

    def fulfilled(self):
        """
        Determines if Block is fulfilled.
        """
        return self.data is not None
