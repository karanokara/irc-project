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

# if len(sys.argv) < 2:
#     print ("USAGE:   echo_server_sockets.py <PORT>")
#     sys.exit(0)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''
# port = int(sys.argv[1])
port = 2999
backlog = 5
size = 1024 * 100       # accept 100k

# bind local source port to socket
server.bind((host,port))

# enable socket to accept connections
server.listen(5)

# input = [server,sys.stdin]
input_list = [server]
running = 1
client_count = 0

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
            print('client #',client_count, ' is at', ip_addr)

            input_list.append(new_socket_conn)

        elif input == sys.stdin:
            # handle standard input

            junk = sys.stdin.readline()
            running = 0 

        else:
            # handle socket conn, s is a socket conn

            data = input.recv(size)
            if data:

                updata = to_upper(data.decode('utf-8'))
            
                print('sending data ', updata)
                data_from = '@Server >'
                send_data = data_from + updata
                input.send(send_data.encode('utf-8'))
            else:
                # close socket conn

                # find out who disconnect
                print('client #', input_list.index(input), ' disconnected.')
                
                input.close()
                input_list.remove(input)

server.close()
