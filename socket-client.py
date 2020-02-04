#!/usr/bin/python
'''
A socket client that can make a connection

USAGE:   python socket-client.py <HOST> <PORT> <MESSAGE>
EXAMPLE: python socket-client.py localhost 8000 Hello
'''
import socket
import sys

if len(sys.argv) < 4:
    print ("USAGE: echo_client_sockets.py <HOST> <PORT> <MESSAGE>")
    sys.exit(0)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = sys.argv[1]
port = int(sys.argv[2])
close = 0

# initiate conn on a socket
s.connect((host,port))

while(not close):
    # send data
    s.send(sys.argv[3].encode('utf-8'))

    # receive data in byte
    data = s.recv(10000000)

    print (data.decode('utf-8'))
    print ('received', len(data), ' bytes')

    s.close()
