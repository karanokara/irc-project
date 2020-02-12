#!/usr/bin/python
'''
A socket client that can make a connection

USAGE:   python3 socket-client.py <HOST> <PORT>
USAGE:   python socket-client.py <HOST> <PORT>
EXAMPLE: python3 socket-client.py localhost 2999
EXAMPLE: python socket-client.py localhost 2999
'''
import socket   # the socket API to creat a "door"
import sys
import select  # supports asynchronous I/O on multiple file descriptors

if len(sys.argv) < 3:
    print ("USAGE: python3 socket-client.py <HOST> <PORT>")
    sys.exit(0)

# A client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# conn timeout to 5 seconds
# client.settimeout(5)

host = sys.argv[1]
port = int(sys.argv[2])
size = 1024 * 100  # accept 100k
username = 'client'


def prompt(username):
    '''A function to print out prompt for client
    '''
    print(f'> {username} $ ', end='', flush=True)    # don't go to next line, allow input


def greet_client(client_socket,username):
    ''' send server the name of client'''
    done = 0

    while not done:
        print(f'Enter your name: ', end='', flush=True)
        username = sys.stdin.readline().rstrip()
        send_data = 'USER ' + username
        client_socket.send(send_data.encode('utf-8'))

        try:
            res_data = client_socket.recv(size).decode('utf-8').rstrip()
        except:
            # can't receive from server
            sys.exit('\nDisconnected from the server. ')
        
        status = res_data[0:3]      # get status code
        res_data = res_data[4:]     # the leaving msg

        print()
        print(res_data)
        print()

        if (status == '200'):
            done = 1

    prompt(username)
    return username


# try initiate conn on a socket
try:
    print('Connecting...')
    client.connect((host, port))
except:
    sys.exit(f'Error: Fail to connect to host: {host} on port: {port}.')

print(f'Connected successfully.')

# greet client to the server
username = greet_client(client, username)


# a list of input steams
input_list = [client, sys.stdin]    # if executed in linux
# input_list = [client]   # in window


while (1):
    # Get the list sockets that are ready to read
    read_ready,write_ready,except_ready = select.select(input_list, [], [])

    # loop the input that get in
    for input in read_ready:

        if input == client:
            # input is from the client socket from remote server

            # receive data
            try:
                res_data = input.recv(size)
            except:
                # can't receive from server
                sys.exit('\nDisconnected from the server.')

            if res_data:

                status = res_data[0:3]      # get status code
                res_data = res_data[4:]     # the leaving msg

                # print data in a new line
                print()
                print(res_data.decode('utf-8'))
                print()

                prompt(username)
                # print ('received', len(res_data), ' bytes')
            else:
                # there is no data, server is disconnected
                sys.exit('\nDisconnected from the server.')

        else:
            # input is from client keyboard input
            send_data = sys.stdin.readline()

            if send_data == 'quit\n':
                client.close()
                sys.exit('\nYou exit successfully.')
            
            # send data
            client.send(send_data.encode('utf-8'))


