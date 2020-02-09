#!/usr/bin/python
'''
A socket server that handle connecting clients

Entering any line of input at the terminal will exit the server.

USAGE:   python3 socket-server.py <PORT>
USAGE:   python socket-server.py <PORT>
EXAMPLE: python3 socket-server.py 2999
EXAMPLE: python socket-server.py 2999
'''
import socket
import select   # handle multiple clients at a time.
import sys


# if len(sys.argv) < 2:
#     print ("USAGE:   echo_server_sockets.py <PORT>")
#     sys.exit(0)



''' --------------------- Message functions ---------------------------- '''


def USER(username, client):
    '''Creat a user for a current client
       USAGE: USER <username>
    '''
    for client_socket in client_book:
        if client_book[client_socket].name == username:
            send_error(f'User {username} already exist', client)
            return 0

    # username not exist, add it to client book
    client_book[client] = {
        'name': username,
        'room': False,
        'socket': client
    }

    data = f'Welcome {username}!\n'
    data += get_help_msg()
    client.send(data.encode('utf-8'))


def LIST(msg, client):
    '''Listing rooms
       USAGE: LIST <room name>    
    '''
    data = 'list'
    client.send(data.encode('utf-8'))


def ROOM(msg, client):
    '''Create a rooms
       USAGE: ROOM <room name>
    
    '''

    data = 'ROOM'
    client.send(data.encode('utf-8'))


def JOIN(msg, client):
    '''Join a room
       USAGE: JOIN <room name>

    '''
    data = 'JOIN'
    client.send(data.encode('utf-8'))
    

def LEVE(msg, client):
    '''Leave a room
       USAGE: LEVE <room name>
    
    '''
    data = 'LEVE'
    client.send(data.encode('utf-8'))
    



''' --------------------- Tool functions ---------------------------- '''


# a function table
msg_options = {
    'USER': USER,
    'LIST': LIST,
    'ROOM': ROOM,
    'JOIN': JOIN,
    'LEVE': LEVE
}

def to_upper(string):
    upper_case = ""
    for character in string:
         if 'a' <= character <= 'z':
             location = ord(character) - ord('a')
             new_ascii = location + ord('A')
             character = chr(new_ascii)
         upper_case = upper_case + character
    return upper_case


def analyze_msg(msg, client):
    '''A function to analyze the msg and call an appropriate function
        using a function table msg_options

        message format: COMD msg        (length is at leaset 6)
    '''
    msg = msg.strip()
    if len(msg) < 6: 
        send_error('Invalid message.', client)
    else:
        directive = to_upper(msg[0:4])
        later_msg = msg[5:]
        try:
            msg_options[directive](later_msg, client)
        except:
            send_error('Unknown message command.', client)



def disconnet_client(input_list, client_count, input):
    ''' find out who disconnect'''

    print('client #' + str( input_list.index(input)) + ' disconnected.')
    
    # inform clients in a same room who has disconnected
    # TODO

    # close socket conn
    input.close()
    input_list.remove(input)
    client_count -= 1


def get_client_info(client_list, client):

    return {}


def send_error(msg, client):
    '''Send an error msg to client
    '''
    msg = f'<<<< Error: {msg} >>>>'
    client.send(msg.encode('utf-8'))


def broadcast(socket, room, client, msg):
    '''Broadcase a message to all clients in a room
    '''
    print(f'Broadcast [{msg}] to room [{room}]')
    msg = msg.encode('utf-8')
    socket.send(msg)


def get_help_msg():
    '''Return command instruction'''
    msg = '\nUsage: \n' 
    msg += '       list <room name> - Listing all rooms\n'
    msg += '       room <room name> - Create a rooms\n'
    msg += '       join <room name> - Join a rooms\n'
    msg += '       leve <room name> - Leave a rooms\n'

    return msg




''' --------------------- Program begin here ---------------------------- 
client_info = {
    'name': <username>,
    'room': <room name>, 
    'socket': <client_socket>
}
client_book = {
    <client_socket>: client_info,
    <client_socket>: client_info,
    ...
}
room_book = {
    'room_name': {
        'name': <room name>,
        'clients': [<client_info>, <client_info>, ...]
    }
}

'''



host = ''
# port = int(sys.argv[1])
port = 2999
size = 1024 * 100       # accept 100k
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket server
# input_list = [server,sys.stdin]     # linux
input_list = [server]               # window
running = 1
client_count = 0
client_book = {}
room_book = {}


# bind local source port to socket
server.bind((host,port))

# enable socket to accept connections
server.listen(5)

print('Server is now running ...')

while running:
    # code stop below
    # once there is client socket conn, code move forward
    read_ready,write_ready,except_ready = select.select(input_list,[],[])

    for input in read_ready:

        if input == server:
            # handle the server socket
            
            new_socket_conn, ip_addr = server.accept()

            client_count += 1
            print('client #' + str(client_count) + ' is at', ip_addr)

            # add new client to the listenning list
            input_list.append(new_socket_conn)

        elif input == sys.stdin:
            # handle standard input

            junk = sys.stdin.readline()
            running = 0
            break
        else:
            # handle input comes from socket conn
            try:
                data = input.recv(size)
            except:
                # couldn't receive data, client disconnects
                disconnet_client(input_list, client_count, input)
                
            if data:
                # there is any data from client
                data = data.decode('utf-8').rstrip()
                
                # log the msg
                print('Received data from client #' + str( input_list.index(input)) + ':', data)
                
                # analyze the msg and call a appropriate function to handle it
                analyze_msg(data, input)

                # send_data = data_from + updata
                # input.send(send_data.encode('utf-8'))
            else:
                # there is no data, client disconnects
                disconnet_client(input_list, client_count, input)

                
server.close()
