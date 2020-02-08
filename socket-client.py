#!/usr/bin/python
'''
A socket client that can make a connection

USAGE:   python socket-client.py <HOST> <PORT>
EXAMPLE: python socket-client.py localhost 2999
'''
import socket
import sys
import select  # supports asynchronous I/O on multiple file descriptors

# if len(sys.argv) < 4:
#     print ("USAGE: python socket-client.py <HOST> <PORT> <MESSAGE>")
#     sys.exit(0)

# A client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# conn timeout to 5 seconds
client.settimeout(5)

# host = sys.argv[1]
# port = int(sys.argv[2])
host = '192.168.0.2'
port = 2999
size = 1024 * 100  # accept 100k
username = 'client'


def prompt(username):
    '''A function to print out prompt for client
    '''
    print(f'@{username} $ ', end='', flush=True)    # don't go to next line, allow input

    
# try initiate conn on a socket
try:
    client.connect((host, port))
except:
    sys.exit(f'Error: Fail to connect to host: {host} on port: {port}.')

# a list of input steam
input_list = [client, sys.stdin]    # if executed in linux
# input_list = [client]   # in window

while (1):
    # Get the list sockets that are ready to read
    read_ready,write_ready,except_ready = select.select(input_list, [], [])

    # loop the input that get in
    for input in read_ready:

        # input is from the client socket from remote server
        if input == client:

            # receive data
            res_data = input.recv(size)

            # print data in a new line
            print()
            print(res_data.decode('utf-8'))
            
            print()
            prompt(username)
            # print ('received', len(res_data), ' bytes')

        else:
            # from client input
            send_data = sys.stdin.readline()

            if send_data == 'quit\n':
                client.close()
                sys.exit('<<<< You exit successfully.')

            send_data += '\r\n'
            
            # send data
            client.send(send_data.encode('utf-8'))
            prompt(username)


