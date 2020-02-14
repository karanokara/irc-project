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
BUFFER_SIZE = 1024 * 100  # accept 100k
username = 'client'


def prompt(username):
    '''A function to print out prompt for client
    '''
    print(f'> {username} $ ', end='', flush=True)    # don't go to next line, allow input


def analyze_msg(msg, client):
    ''' Analyze a msg from client
    '''
    # Quit the app
    if str.upper(send_data) == 'QUIT\n':
        client.close()
        sys.exit('\nYou exit successfully.')

    # For sending file
    if str.upper(msg[0:4]) == 'FILE':
        params = str.split(str.strip(msg), ' ')
        if not (len(params) == 3):
            print('\nError: Invalid parameter, see HELP.\n')
            prompt(username)
            return 0
        
        filename = params[2]
        try:
            file_stream = open(filename,'rb')
        except:
            print('\nError: File doesn\'t exist.\n')
            prompt(username)
            return 0
        
        
        client.send(msg.encode('utf-8'))  # send msg
        
        # receive server response
        try:
            server_response = client.recv(BUFFER_SIZE).decode('utf-8')
        except:
            print('\nError: Failed to send file. server no response\n')
            prompt(username)
            return 0

        # if server ready to receive the file
        if(server_response[0:3] == '100'):      
            # prepare file
            file_byte = file_stream.read(BUFFER_SIZE)
            file_stream.close()
        
            # send file
            client.send(file_byte)
        else:
            print()
            print(server_response[4:])
            print()
            prompt(username)


        return 0
    
    # send data
    client.send(msg.encode('utf-8'))


def analyze_res(res_data,client):
    ''' Analyze a response from server
    '''
    res_data = res_data.decode('utf-8')
    status = res_data[0:3]      # get status code
    res_data = res_data[4:]     # the leaving msg

    # continue to rend a file
    if status == '102':

        # let server send the file here
        client.send('100'.encode('utf-8'))

        try:
            msgs = str.split(res_data, ' ', 2)
            filename = msgs[0]
            file_size = msgs[1]
            res_data = msgs[2]
            file_byte = client.recv(BUFFER_SIZE)
            while len(file_byte) < int(file_size):
                file_byte += client.recv(BUFFER_SIZE)

        except:
            print('Failed to receive the file.')
            return 0

        # create the file
        filename = 'receive_' + filename
        file_stream = open(filename, 'wb')
        file_stream.write(file_byte)
        file_stream.close()
        
    # print data in a new line
    print()
    print(res_data)
    print()

    prompt(username)
    # print ('received', len(res_data), ' bytes')




def greet_client(client_socket,username):
    ''' send server the name of client'''
    done = 0

    while not done:
        print(f'Enter your name: ', end='', flush=True)
        username = sys.stdin.readline().rstrip()
        send_data = 'USER ' + username
        client_socket.send(send_data.encode('utf-8'))

        try:
            res_data = client_socket.recv(BUFFER_SIZE).decode('utf-8').rstrip()
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
                res_data = input.recv(BUFFER_SIZE)
            except:
                # can't receive from server
                sys.exit('\nDisconnected from the server.')

            if res_data:
                # analyze the response data
                analyze_res(res_data, client)
                
            else:
                # there is no data, server is disconnected
                sys.exit('\nDisconnected from the server.')

        else:
            # input is from client keyboard input
            send_data = sys.stdin.readline()

            analyze_msg(send_data, client)


