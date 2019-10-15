# Name (Student ID):
Eric Ngo (917905955)

# Project Name: 
Multithreaded Client/Server TCP Message App With Primitive Sockets. 

# Grades

100/100 + 2 % extra credit

Comments:

* You missunderstood what the client id is in option 1, the client id is the socket id provided by the server to that client when it connects, and you need to show it in the client console log

* Option 5 not working on my end. The client connected to the new channel is not receiving messages. This is suppose to be similar to a P2P connections between client-client 

* Good docs in README file. 

#

# Project Description:
The scope of this project was to create a TCP Message App. The architecture is that of a client-server architecture, where a client can connect to a server and send messages to other users. The server saves all of the connected clients and their messages, and handles connecting and disconnecting clients. The TCPClientHandler is suppose to be an interface between the client and the server, whereby the TCPClientHandler handles the application logic and uses the client to send and receiving information from the server. The server receives requests and performs the proper instructions.

The Client class handles connecting, sending, and retrieving from the server/channel. All of the functions are documented in code.

The TCPClientHandler class handles implementing the application logic, using the Client object for interfacing with the server. All of the functions are documented in code.

The Server class handles the back-end server logic, receiving a client's request, performing the proper instructions, and sending the proper requests. All of the functions are documented in code.

The Channel class handles the back-end channel logic, whereby clients can connect to a new channel and chat with each other. All of the functions are documented in code.

The helpers.py file holds logic that is generally used across all classes. All of the functions are documented in code.

Notes:  
Extra Credit 1: The login feature that I implemented is that client's ids are the names that they input after running `python3 client.py`. On first login, the server saves the client's password onto the server. On re-login, the server matches the given client id's password to the one on the server. If there is a match, it allows connection. If there is an error, the client is asked to put in the password again.  

# Project Purpose:
This project's purpose was to get more familiar with Python socket programming, and multi-threaded programming. Also to get more familiar with the client-server architecture and the scope of the responsibilities of the clients and servers.

# Installation/Execution Instructions:
Installation:  
Make sure to have python 3.6.8 installed: https://www.python.org/downloads/release/python-368/.  
clone this repo: `git clone https://github.com/sfsu-joseo/csc645-01-fall2019-projects-savingPrivateEric.git`  

Execution:  
For this project, there are two main scripts of interest: server.py and client.py.  
cd to proper root directory: `cd applications/tcp-message-app`  
start the server: `python3 server.py`  
Enter server's ip and port information.  
start the client(s): `python3 client.py`  
Enter server's ip and port information.  

# Compatiblity Issues:
Python 3.6.8 64-bit. This code was tested on Ubuntu 18.04.3 LTS 64-bit.

Known Issues: n/a

# Challenges:
Coming in to this class, I did not have 415 experience, so it was a small challenge to learn the required knowledge to do multi-threaded programming. Another challenge I've faced was how to optimize my code, as well as what the pattern for broadcasting messages was. All other challenges were syntax challenges.

Fortunately, I was able to figure out all of my issues.
