#!/usr/bin/python
'''
A socket server that handle connecting clients

Entering any line of input at the terminal will exit the server.

USAGE:   python socket-server.py <PORT>
EXAMPLE: python socket-server.py 8000
'''
import socket
import select   # handle multiple clients at a time.
import sys

def to_upper(string):
    upper_case = ""
    for character in string:
         if 'a' <= character <= 'z':
             location = ord(character) - ord('a')
             new_ascii = location + ord('A')
             character = chr(new_ascii)
         upper_case = upper_case + character
    return upper_case

if len(sys.argv) < 2:
    print ("USAGE:   echo_server_sockets.py <PORT>")
    sys.exit(0)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''
port = int(sys.argv[1])
backlog = 5
size = 1024 * 100       # accept 100k

# bind local source port to socket
server.bind((host,port))

# enable socket to accept connections
server.listen(5)

# input = [server,sys.stdin]
input = [server]
running = 1
client_count = 0

while running:
    inputready,outputready,exceptready = select.select(input,[],[])

    for s in inputready:

        if s == server:
            # handle the server socket
            
            new_socket_conn, ip_addr = server.accept()

            ++client_count
            print('client #',client_count, ' is at', ip_addr)

            input.append(new_socket_conn)

        elif s == sys.stdin:
            # handle standard input

            junk = sys.stdin.readline()
            running = 0 

        else:
            # handle socket conn, s is a socket conn

            data = s.recv(size)
            if data:

                updata = to_upper(data.decode('utf-8'))
            
                print('sending data ', updata)
                s.send(updata.encode('utf-8'))
            else:
                # close socket conn
                s.close()
                input.remove(s)

server.close()
