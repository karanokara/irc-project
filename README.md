
# IRC (Internet Relay Chat)

IRC or Internet Relay Chat is an application that lets multiple users communicate via text messages with each other in common "virtual" rooms.

This program is a CLI(command line interface)-based application.

## Overview
1. Implementing an IRCclient and server from scratch in this project using whatever programming language.

2. In charge of all of the protocol specifications and functionality of IRC application. 

3. Basic functionalities:
    + [x] supprot mulitple client connecting to server as a user
    + [x] list rooms available
    + [x] list members of a room
    + [x] create a room
    + [x] join multiple rooms
    + [x] leave a room
    + [x] send message to a specific room
    + [x] private message
    + [x] client disconnect from server
    + [x] server can disconnect 
    + [x] client, server handle crash from each other

4. Other features:
    + [x] File transfer
    + [x] Secure messaging
    + [x] Cloud connected server
    - etc

5. Refer to the IRC project grading criteria

6. Not Graphical user interfaces

7. Turn in an RFC-style document that describes IRC protocol (describe the format of the messages that the client and server will exchange in order to properly implement the IRC application). 

8. An example RFC is the IRC RFC 1459: https://tools.ietf.org/html/rfc1459


## Run the program

###### Install

``` py
pip install -r requirements.txt
```

###### Run server

``` py
python3 socket-server.py <PORT>
python socket-server.py <PORT>
```

###### Run client

``` py
python3 socket-client.py <HOST> <PORT>
python socket-client.py <HOST> <PORT>
```

