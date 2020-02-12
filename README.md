
# IRC (Internet Relay Chat)

IRC or Internet Relay Chat is an application that lets multiple users communicate via text messages with each other in common "virtual" rooms.

## Tasks
1. Implementing an IRCclient and server from scratch in this project using whatever programming language.

2. In charge of all of the protocol specifications and functionality of IRC application. 

3. Basic functionalities:
    + supprot mulitple client connecting to server as a user
    + list rooms available
    + list members of a room
    + create a room
    + join multiple rooms
    + leave a room
    + send message to a specific room
    + private message
    + client disconnect from server
    + server can disconnect 
    + client, server handle crash from each other

4. Other features:
    - File transfer
    - Secure messaging
    + Cloud connected server
    - etc

5. Refer to the IRC project grading criteria

6. Not Graphical user interfaces

7. Turn in an RFC-style document that describes IRC protocol (describe the format of the messages that the client and server will exchange in order to properly implement the IRC application). 

8. An example RFC is the IRC RFC 1459: https://tools.ietf.org/html/rfc1459


## Program

###### server

```
python3 socket-server.py <PORT>
python socket-server.py <PORT>
```

###### client

```
python3 socket-client.py <HOST> <PORT>
python socket-client.py <HOST> <PORT>
```

