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
    ''' Creat a user for a current client

        USAGE: USER <username>
    '''
    # if user already in the book
    if CLIENT_BOOK.__contains__(client):
        send_error('300',f'You already login.', client)
        return 0

    # check if username have already been used by other users
    for client_socket in CLIENT_BOOK:
        if CLIENT_BOOK[client_socket]['name'] == username:
            send_error('300',f'User "{username}" already exist', client)
            return 0

    # inform other users
    broadcast([], f'Client "{username}" login.')

    # username not exist, add it to client book
    CLIENT_BOOK[client] = {
        'name': username,
        'rooms': [],
        'socket': client
    }

    data = '200 '
    data += f'Welcome {username}!\n\n'
    data += get_help_msg()
    client.send(data.encode('utf-8'))


def LIRO(msg, client):
    ''' Listing all rooms with their name

        USAGE: LIRO
    '''
    if not (validate_user(client)):
        return 0

    data = '200 '
    if len(ROOM_BOOK) > 0:
        data += 'Available rooms:\n'
        for room in ROOM_BOOK:
            data += '                 ' + ROOM_BOOK[room]['name'] + '\n'
    else:
        data += 'There is no rooms.'        
    client.send(data.encode('utf-8'))


def LIME(room_name, client):
    ''' Listing member in a room

        USAGE: LIME <room name>    
    '''
    if not (validate_user(client)):
        return 0
        
    if (len(str.split(room_name,' ')) > 1 or len(room_name) == 0):
        send_error('400','Invalid room name.', client)
        return 0

    if not ROOM_BOOK.__contains__(room_name):
        send_error('300',f'Room "{room_name}" is not exist.', client)
        return 0

    client_list = ROOM_BOOK[room_name]['clients']

    data = '200 '
    data += 'Current users:\n'
    for user in client_list:
        data += '               ' + user['name'] + '\n'

    client.send(data.encode('utf-8'))


def ROOM(room_name, client):
    ''' Create a rooms

        USAGE: ROOM <room name>
    '''
    if not (validate_user(client)):
        return 0

    # if it contains only 1 word for room name
    if (len(str.split(room_name,' ')) > 1 or len(room_name) == 0):
        send_error('400','Invalid room name.', client)
        return 0
    
    for room in ROOM_BOOK:
        if ROOM_BOOK[room]['name'] == room_name:
            send_error('300', f'Room "{room_name}" already exist.', client)
            return 0

    # clear to create a new room
    ROOM_BOOK[room_name] = {
        'name': room_name,
        'clients': []
    }

    data = '200 '
    data += f'Room "{room_name}" successfully created.'
    client.send(data.encode('utf-8'))


def JOIN(room_name, client):
    ''' Join a room

        USAGE: JOIN <room name>
    '''
    if not (validate_user(client)):
        return 0

    if (len(str.split(room_name,' ')) > 1 or len(room_name) == 0):
        send_error('400','Invalid room name.', client)
        return 0

    if not ROOM_BOOK.__contains__(room_name):
        send_error('300',f'Room "{room_name}" is not exist.', client)
        return 0

    client_list = ROOM_BOOK[room_name]['clients']
    current_client = CLIENT_BOOK[client]
    username = current_client['name']

    # room is exist, check if client alread inside
    if current_client in client_list:
        send_error('300',f'Client "{username}" already exist in the room "{room_name}".', client)
        return 0

    # inform other users that this user join the room
    broadcast([room_name], f'\n"{username}" joined the room "{room_name}"')

    # room is exist, client not inside that room, add client
    client_list.append(current_client)

    # add room to client
    current_client['rooms'].append(room_name)

    # inform current client
    data = '200 '
    data += f'You have joined the room "{room_name}"'
    client.send(data.encode('utf-8'))
    

def LEVE(room_name, client):
    ''' Leave a room

        USAGE: LEVE <room name>
    '''
    if not (validate_user(client)):
        return 0

    if (len(str.split(room_name,' ')) > 1 or len(room_name) == 0):
        send_error('400','Invalid room name.', client)
        return 0

    if not ROOM_BOOK.__contains__(room_name):
        send_error('300',f'Room "{room_name}" is not exist.', client)
        return 0

    client_list = ROOM_BOOK[room_name]['clients']
    current_client = CLIENT_BOOK[client]
    username = current_client['name']

    # room is exist, check if client inside
    if not (current_client in client_list):
        send_error('300',f'Client "{username}" doesn\'t exist in the room "{room_name}".', client)
        return 0

    # room is exist, client inside room, remove client
    client_list.remove(current_client)

    # remove room from client
    current_client['rooms'].remove(room_name)

    # inform other users that this user leave the room
    broadcast([room_name], f'\n"{username}" just leave the room "{room_name}"')

    # inform current client
    data = '200 '
    data += f'You have leave the room {room_name}'
    client.send(data.encode('utf-8'))
    

def SEND(msg, client):
    ''' Send a message to a room

        USAGE: SEND <room name> <msg>
    '''
    if not (validate_user(client)):
        return 0

    msgs = str.split(msg, ' ',1)
    if not (len(msgs) == 2 and len(msgs[0]) > 0 and len(msgs[1]) > 0 ):
        send_error('400','Invalid parameter, see HELP.', client)
        return 0

    room_name = msgs[0]
    msg = msgs[1]

    # check if room exists
    if not ROOM_BOOK.__contains__(room_name):
        send_error('300',f'Room "{room_name}" is not exist.', client)
        return 0    

    client_list = ROOM_BOOK[room_name]['clients']
    current_client = CLIENT_BOOK[client]
    username = current_client['name']

    # room is exist, check if client inside
    if not (current_client in client_list):
        send_error('300',f'Client "{username}" doesn\'t exist in the room "{room_name}".', client)
        return 0    

    # send msg to all clients in the room
    for user in client_list:
        if not (user == current_client):
            # send to target
            data = '200 '
            data += f'\n{username}@{room_name}: ' + msg
            user['socket'].send(data.encode('utf-8'))

    # send to current user
    data = '200 '
    data += f'You@{room_name}: ' + msg
    client.send(data.encode('utf-8'))
    return 1


def PRIV(msg, sender):
    ''' Send a private message to a client

        USAGE: PRIV <username> <msg>
    '''
    if not (validate_user(sender)):
        return 0

    msgs = str.split(msg, ' ',1)
    if not (len(msgs) == 2 and len(msgs[0]) > 0 and len(msgs[1]) > 0 ):
        send_error('400','Invalid parameter, see HELP.', sender)
        return 0

    target_username = msgs[0]
    msg = msgs[1]

    # check if user exists
    for client_socket in CLIENT_BOOK:
        if CLIENT_BOOK[client_socket]['name'] == target_username:
            # send msg to target user
            current_username = CLIENT_BOOK[sender]['name']
            data = '200 '
            data += f'\n{current_username} -> You: ' + msg
            CLIENT_BOOK[client_socket]['socket'].send(data.encode('utf-8'))

            # send msg to current user
            data = '200 '
            data += f'You -> {target_username}: ' + msg
            sender.send(data.encode('utf-8'))
            return 1

    send_error('300',f'User "{target_username}" doesn\'t exist', sender)
    return 0


def FILE(msg, sender):
    ''' Send a file to a client

        USAGE: FILE <username> <filename>
    '''
    global BUFFER_SIZE
    
    if not (validate_user(sender)):
        return 0

    msgs = str.split(msg, ' ',1)
    if not (len(msgs) == 2 and len(msgs[0]) > 0 and len(msgs[1]) > 0 ):
        send_error('400','Invalid parameter, see HELP.', sender)
        return 0

    receiver_name = msgs[0]
    filename = msgs[1]

    # check if user exists
    for client_socket in CLIENT_BOOK:
        if CLIENT_BOOK[client_socket]['name'] == receiver_name:
            sender_name = CLIENT_BOOK[sender]['name']
            receiver = CLIENT_BOOK[client_socket]
            
            # receive file
            try:
                file_byte = sender.recv(BUFFER_SIZE)
            except:
                send_error('101','Failed to send file.', sender)
                return 0

            # send msg to target user
            data = '102 '
            data += f'\nClient "{sender_name}" send you a file "{filename}"'
            receiver['socket'].send(data.encode('utf-8'))
            
            # send file
            receiver['socket'].send(file_byte)
            
            # send msg to current user
            data = '200 '
            data += f'You have sent a file "{filename}" to user "{receiver_name}"'
            sender.send(data.encode('utf-8'))
            return 1

    send_error('300',f'User "{receiver_name}" doesn\'t exist', sender)
    return 0
    

def HELP(msg, client):
    ''' Print out command help

        USAGE: HELP
    '''
    data = '200 '
    data += get_help_msg()
    client.send(data.encode('utf-8'))



''' --------------------- Tool functions ---------------------------- '''


# a function table
msg_options = {
    'USER': USER,
    'LIRO': LIRO,
    'LIME': LIME,
    'ROOM': ROOM,
    'JOIN': JOIN,
    'LEVE': LEVE,
    'SEND': SEND,
    'PRIV': PRIV,
    'FILE': FILE,
    'HELP': HELP
}


def get_help_msg():
    ''' Return command instruction'''
    msg = 'Usage: \n' 
    msg += '       LIRO                         - Listing all rooms\n'
    msg += '       LIME <room name>             - Listing members in a room\n'
    msg += '       ROOM <room name>             - Create a room\n'
    msg += '       JOIN <room name>             - Join a room\n'
    msg += '       lEVE <room name>             - Leave a rooms\n'
    msg += '       SEND <room name> <msg>       - Send message to a room\n'
    msg += '       PRIV <username> <msg>        - Send private message to a client\n'
    msg += '       FILE <username> <filename>   - Send private message to a client\n'
    msg += '       HELP                         - Get command help\n'
    msg += '       QUIT                         - Quit the application\n'

    return msg


def to_upper(string):
    ''' string to uppercase '''
    upper_case = ""
    for character in string:
         if 'a' <= character <= 'z':
             location = ord(character) - ord('a')
             new_ascii = location + ord('A')
             character = chr(new_ascii)
         upper_case = upper_case + character
    return upper_case


def analyze_msg(msg, client):
    ''' A function to analyze the msg and call an appropriate function
        using a function table msg_options

        message format: COMD msg        (length is at leaset 4)
    '''
    msg = msg.strip()
    if len(msg) < 4: 
        send_error('400', 'Invalid message.', client)
    else:
        directive = to_upper(msg[0:4])
        later_msg = msg[5:]
        try:
            msg_options[directive](later_msg, client)
        except:
            send_error('500', 'Unknown message command. See HELP.', client)


def disconnet_client(INPUT_LIST, input):
    ''' Disconnect a client
    '''
    global CLIENT_COUNT

    username = CLIENT_BOOK[input]['name']

    print(f'client "{username}" disconnected.')

    # clear client stored info
    room_list = CLIENT_BOOK[input]['rooms']
    for room in room_list:
        ROOM_BOOK[room]['clients'].remove(CLIENT_BOOK[input])

    # remove client
    CLIENT_BOOK.pop(input)

    # inform other users
    broadcast([], f'Client "{username}" logout.')

    # close socket conn
    input.close()                   # close socket
    INPUT_LIST.remove(input)        # remove socket
    CLIENT_COUNT -= 1


def send_error(status, msg, client):
    ''' Send an error msg to client
    '''
    msg = f'{status} Error: {msg}'
    client.send(msg.encode('utf-8'))


def validate_user(client):
    ''' Validate if a user is in the book
    '''
    if (client in CLIENT_BOOK):
        return True
    else:
        send_error('600', 'Client is not valid.', client)
        return False


def broadcast(rooms, msg):
    ''' Broadcast a msg to all clients or to some specific
        rooms if length or rooms list > 0

        arg:

        rooms - a list of room name

        msg - a msg string
    '''
    # broadcast to all clients
    if len(rooms) == 0:
        for socket in CLIENT_BOOK:
            data = '200 '
            data += msg
            CLIENT_BOOK[socket]['socket'].send(data.encode('utf-8'))
        return 0

    # broadcast to some specific rooms
    while len(rooms) > 0:
        room_name = rooms.pop(0)
        if ROOM_BOOK.__contains__(room_name):
            client_list = ROOM_BOOK[room_name]['clients']
            for user in client_list:
                data = '200 '
                data += msg
                user['socket'].send(data.encode('utf-8'))





''' --------------------- Program begin here ---------------------------- 
Some data structures:

    client_info = {
        'name': <username>,
        'rooms': [<room name>, <room name>, ...]
        'socket': <client_socket>
    }
    
    CLIENT_BOOK = {
        <client_socket>: client_info,
        <client_socket>: client_info,
        ...
    }

    ROOM_BOOK = {
        'room_name': {
            'name': <room name>,
            'clients': [<client_info>, <client_info>, ...]
        }
    }


error code:
101 fail to send file
102 prepare to receive file
200 OK msg
300 something already exist
400 something invalid
500 something unknown
600 client not valid

'''


# globa variables:
host = ''
# port = int(sys.argv[1])
port = 2999
BUFFER_SIZE = 1024 * 100       # accept 100k
running = 1
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket server
# INPUT_LIST = [server,sys.stdin]     # linux
INPUT_LIST = [server]               # window
CLIENT_COUNT = 0
CLIENT_BOOK = {}
ROOM_BOOK = {}


# bind local source port to socket
server.bind((host,port))

# enable socket to accept N connections
server.listen(5)

print('Server is now running ...')

while running:
    # code stop below
    # once there is client socket conn, code move forward
    read_ready,write_ready,except_ready = select.select(INPUT_LIST,[],[])

    for input in read_ready:

        if input == server:
            # handle the server socket
            
            new_socket_conn, ip_addr = server.accept()

            CLIENT_COUNT += 1
            print('client #' + str(CLIENT_COUNT) + ' is at', ip_addr)

            # add new client to the listenning list
            INPUT_LIST.append(new_socket_conn)

        elif input == sys.stdin:
            # handle standard input

            junk = sys.stdin.readline()
            running = 0
            break
        else:
            # handle input comes from socket conn
            try:
                data = input.recv(BUFFER_SIZE)
            except:
                # couldn't receive data, client disconnects
                disconnet_client(INPUT_LIST, input)
                
            if data:
                # there is any data from client
                data = data.decode('utf-8').rstrip()
                
                # log the msg
                print('Received data from client #' + str( INPUT_LIST.index(input)) + ':', data)
                
                # analyze the msg and call a appropriate function to handle it
                analyze_msg(data, input)

                # send_data = data_from + updata
                # input.send(send_data.encode('utf-8'))
            else:
                # there is no data, client disconnects
                disconnet_client(INPUT_LIST, input)

                
server.close()
