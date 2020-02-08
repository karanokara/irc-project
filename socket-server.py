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

def broadcast(socket, room, client, msg):
    '''Broadcase a message to all clients in a room
    '''
    print(f'Broadcast [{msg}] to room [{room}]')
    msg = msg.encode('utf-8')
    socket.send(msg)




def USER():
    '''Creat a user to the current login user'''
    return 1

def LIST():
    '''Listing rooms'''
    return 1

def ROOM():
    return 1

def JOIN():
    '''Join a room'''
    return 1

def LEVE():
    '''Leave a room'''
    return 1


# a function table
msg_options = {
    'USER': USER,
    'LIST': LIST,
    'ROOM': ROOM,
    'JOIN': JOIN,
    'LEVE': LEVE
}

def analyze_msg(msg, client):
    '''A function to analyze the msg and call an appropriate function
        using a function table msg_options
    '''
    directive = msg[0:4]
    leaving_msg = msg[6:]
    msg_options[directive](leaving_msg, client)


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


''' --------------------- Program begin here ---------------------------- '''



host = ''
# port = int(sys.argv[1])
port = 2999
size = 1024 * 100       # accept 100k
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket server
# input_list = [server,sys.stdin]     # linux
input_list = [server]               # window
running = 1
client_count = 0
client_list = []
room_list = []


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
                print('Receive data from client #' + str( input_list.index(input)) + ':', data)
                
                # analyze the msg and call a appropriate function to handle it
                analyze_msg(data, input)

                # send_data = data_from + updata
                # input.send(send_data.encode('utf-8'))
            else:
                # there is no data, client disconnects
                disconnet_client(input_list, client_count, input)

                
server.close()
