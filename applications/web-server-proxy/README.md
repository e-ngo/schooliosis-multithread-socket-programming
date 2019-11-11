## Instructor Comments

Eric, you did a really good job in this assignment. The only thing that you forgot to implement is when an user enters a url without 'http://' you should validate those cases too, and the client should add it if needed before sending the request. 

Grade: 100/100 plus 2% extracredit added to your final grade.

# Name (Student ID):
Eric Ngo (917905955)

# Project Name: 
Web Proxy Server

# Project Description:
The scope of this project was to create a Web Proxy Server. The architecture is that of a client-server architecture, where a client can connect to a ProxyServer, which performs a GET request to another server, and the client is sent back a proper response. The ProxyServer enforces a set of rules, namely it keeps track of admins and managers ( who can freely access any resource ) and of private_mode_users (who are only allowed to browse in private ).  The ProxyServer supports HTTP/1.0 and HTTP/1.1 persistent and non-persistent connections.

The Client class handles connecting, sending, and retrieving from the ProxyServer. It sends a HTTP request and receives a HTTP response. All of the functions are documented in code.

The ProxyServer class handles accepting a new connection, and employs a ProxyThread to handle the connection logic. All of the functions are documented in code.

The ProxyThread class handles the requests and responses to clients. After the ProxyServer accepts the client, the ProxyThread retrieves its response and determines if the request is persistent or nonpersistent. If persistent, it uses a MAX_NUM_REQUESTS and MAX_TIMEOUT_TIME to determine when to close the connection. After receiving the request, the ProxyThread determines if the client is trying to browse in private or trying to access a blocked resource. It handles the 'login' of a user by checking the credentials passsed in in the request. If the credentials are that of a private_mode_user, the user is able to browse in private mode. If the credentials are that of a manager or admin, the user is able to both browse in private mode and access blocked resources.

The ProxyManager class handles the settings of the ProxyServer. The settings are as follows: the admin, private_mode_user, manager credentials, and sites_blocked are all non-persistent fields. You need to change the hard coded values in the `init_settings` function to their desired values. It saves a history of sites accessed and sites cached persistently by non_private_mode requests. It does this by using the sanitized url of the site as the filename (ie. cache/resources/url.pickle), and the Response object itself into the file. All of the functions are documented in code.

The web-proxy-server.py file is the flask project that implements the view. All of the functions are documented in code.

# Project Purpose:
This project's purpose was to learn about persistent and non-persistent HTTP connections and to learn about the functionalities of a ProxyServer. Also to get more familiar with the client-server architecture and the scope of the responsibilities of the clients and servers.

# Installation/Execution Instructions:
Installation:  
Make sure to have python 3.6.8 installed: https://www.python.org/downloads/release/python-368/.  
clone this repo: `git clone https://github.com/sfsu-joseo/csc645-01-fall2019-projects-savingPrivateEric.git`  

Dependencies:  
Make sure to have the following installed with `pip3 install <dependency name>`:  
- flask
- requests

Execution:    
cd to proper root directory: `cd applications/web-proxy-server`  
start the ProxyServer: `python3 proxy_server/proxy_server.py`  
start the Flask application: `python3 web-proxy-server.py`  
The flask project should be configured for `localhost:5000`.  
Go to `localhost:5000`.  
Type in the url you want to visit to the first input box with placeholder `yoursite`.  
If you want to browse in private_mode, check the `private_mode` button, and pass in the proper email/password credentials.  
If you want to access a blocked resource, pass in the proper email/password credentials.  
To look at ProxyManager settings, nonprivatemode history and cached items, visit `localhost:5000/proxy-settings`.  

# Compatiblity Issues:
Python 3.6.8 64-bit. This code was tested on Ubuntu 18.04.3 LTS 64-bit, with Google Chrome Version 77.0.3865.120 (Official Build) (64-bit).

Known Issues: If the site requested is too large, the socket receive will be unable to read the whole object in one swoop, and pickle.load will truncate the received object, leaving you with an empty object. Please use web pages that are small, ie. `http://example.com`, or even `http://google.com`.  

# Challenges:
A large part of this assignment was to figure out exactly the scopes of each requirements. Given an existing code base (the template), I was to figure out how the components work with respect to the documentation guidelines. Many challenges I have faced were trying to understand how to complete the requirements. Turns out that many times, I would be overthinking the assignment. Other times, I would be passively learning instead of actively learning.  
After starting to think on my own and think more simply, I was able to finish the assignment.
