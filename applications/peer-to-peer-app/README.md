# Name (Student ID):
Eric Ngo (917905955)

# Project Name: 
Peer to Peer Application

# Project Description:
The scope of this project was to implement a semi-decentralized peer-to-peer application in which peers can share torrents with each other.  

# Project Purpose:
This project's purpose is to learn more about the Peer to peer architecture and the importance of peers, trackers, and torrents in this file distribution mechanism. Additionally, it was to introduce the BitTorrent Protocol and the many ways to optimize such networks, ie. using Tit-for-Tat.

# Installation/Execution Instructions:
Installation:  
Make sure to have python 3.6.9 installed: https://www.python.org/downloads/release/python-369/.  
clone this repo: `git clone https://github.com/sfsu-joseo/csc645-01-fall2019-projects-savingPrivateEric.git`  

Execution:    
cd to proper root directory: `cd applications/peer-to-peer-app`  
## Tracker:  
Note that the Tracker defaults to localhost as host_ip, and 50000 as host port. You should either modify this inside the `tracker.py` file as one of the constants, or modify your .torrent files.  
start the Tracker: `python3 tracker.py`  
## Seeders, Leechers/Peers:
The tracker information and path to the file is pulled from the .torrent file you specifcy on running the script. Explanation for how the .torrent file is formatted is shown below.  
start the Seeder peer: `python3 test_seed.py`  
Enter the port to listen to when prompted.  
Enter the path to the torrent file when prompted.  
start the "leecher" peer: `python3 test_peer.py`  
Enter the port to listen to when prompted.  
Enter the path to the torrent file when prompted.  

What should happen is that the swarm information is updated each time a new peer connects to that swarm, and any peers who are interested in downloading from a seeder would constantly poll the tracker for new peers and makes a connection to the new peeres. The seeders are in charge of answering any queries for certain pieces:blocks.  
When the leecher has all the files, it saves the file to the path specified in the torrent file, and becomes a seeder itself.  

## Try it yourself!
First open 3 terminals.
In terminal 1: Start the tracker
```
$ python3 tracker.py
Tracker IP:  127.0.0.1
Tracker Port: 50000
Server started
Listening at 127.0.0.1(50000):
Client ('127.0.0.1', 53434) has connected!
```
In termminal 2: Start the seeder
```
$ python3 test_seed.py
Please input the PORT to listen onto: 60000
Starting p2p as SEED
Path to torrent file: ./random_jpeg_seed.torrent
```
In terminal 3: Start the peer/leecher
```
$ python3 test_peer.py
Please input the PORT to listen onto: 60001
Path to torrent file: ./random_jpeg.torrent
```
If successful, the peer is able to get all of the file, creates a new jpeg to filepath `./download1.jpeg` that is similar to that of `./randommmmm.jpeg`.

# Compatiblity Issues:
Python 3.6.9 64-bit. This code was tested on Ubuntu 18.04.3 LTS 64-bit.

Known Issues: n/a  

# Challenges:
The challenge of this was in the command line interfaces to show live updates, and to throttle the downloaders/receivers. In the interest of time, I decided not to do them.

# Notes:
## Torrent:
```
{
   "announce": "http://127.0.0.1:50000",
   "info": {
      "length": 405431,
      "name": "randommmmm.jpeg",
      "piece length": 16384,
      "path": "./download1.jpeg",
      "pieces": "<hex>9F....</hex>"
   }
}
```
Announce field has: `{tracker_ip}:{tracker_port}`. This is the information used to identify where the tracker is.  
Info field has subfields:  
Info's length: size of whole file in bytes.  
Info's name: Name of resource.  
Info's piece length: how big each pieces are.  
Info's path: If it is a seeder's .torrent file, this is the PATH TO THE COMPLETE FILE. If it is a peer/leecher's .torrent file, this is the PATH TO SAVE THE COMPLETE FILE WHEN DONE.  
Info's pieces: A space delimited hex string with <hex>...</hex> delimiting that string.  
Example: random_jpeg_seed.torrent && random_jpeg.torrent  