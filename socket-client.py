#!/usr/bin/python
'''
A socket client that can make a connection

USAGE:   python socket-client.py <HOST> <PORT> <MESSAGE>
EXAMPLE: python socket-client.py localhost 8000 Hello
'''
import socket
import sys

# if len(sys.argv) < 4:
#     print ("USAGE: echo_client_sockets.py <HOST> <PORT> <MESSAGE>")
#     sys.exit(0)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# host = sys.argv[1]
# port = int(sys.argv[2])
host = 'localhost'
port = 2999
close = 0

# try initiate conn on a socket
try:
    client_socket.connect((host, port))
except:
    sys.exit(f'Error: Fail to connect to host: {host} on port: {port}.')

while (not close):
    
    print('Enter: ', end='', flush=True)
    data = sys.stdin.readline()

    # send data
    client_socket.send(data.encode('utf-8'))

    # receive data in byte
    res_data = client_socket.recv(10000000)

    print (res_data.decode('utf-8'))
    print ('received', len(res_data), ' bytes')

    if data is 'quit':
        close = True

client_socket.close()
