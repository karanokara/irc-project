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
import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

if len(sys.argv) < 3:
    print ("USAGE: python3 socket-client.py <HOST> <PORT>")
    sys.exit(0)


############################# Global Variables ###################################


# A client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# conn timeout to 5 seconds
# client.settimeout(5)

HOST = sys.argv[1]
PORT = int(sys.argv[2])
BUFFER_SIZE = 1024 * 100    # accept 100k
USERNAME = 'client'
KEY = ''                    # a key string use to encrypt/decrypt msg


############################ User functions ########################################



def encrypt(key, source, encode=True):
    ''' Encryp a string using CBC encryption 
        with a key

        Arg:
        key - byte string
        sourece - byte string

        return:
        encoded string
    '''
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
    source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
    return base64.b64encode(data).decode("latin-1") if encode else data


def decrypt(key, source, decode=True):
    ''' Decryp a string using CBC encryption 
        with a key

        Arg:
        key - byte string
        sourece - encoded string

        return:
        byte string
    '''
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = source[:AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])  # decrypt
    padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
    if data[-padding:] != bytes([padding]) * padding:  # Python 2.x: chr(padding) * padding
        raise ValueError("Invalid padding...")
    return data[:-padding]  # remove the padding


def prompt(username):
    '''A function to print out prompt for client
    '''
    print(f'> {username} $ ', end='', flush=True)    # don't go to next line, allow input


def analyze_msg(msg, client):
    ''' Analyze a msg from client
    '''
    # Quit the app
    if str.upper(msg[0:4]) == 'QUIT':
        client.close()
        sys.exit('\nYou exit successfully.')

    # Sending a file
    if str.upper(msg[0:4]) == 'FILE':
        params = str.split(str.strip(msg), ' ')
        if not (len(params) == 3):
            print('\nError: Invalid parameter, see HELP.\n')
            prompt(USERNAME)
            return 0
        
        filename = params[2]
        try:
            file_stream = open(filename,'rb')
        except:
            print('\nError: File doesn\'t exist.\n')
            prompt(USERNAME)
            return 0
        
        
        client.send(msg.encode('utf-8'))  # send msg
        
        # receive server response
        try:
            server_response = client.recv(BUFFER_SIZE).decode('utf-8')
        except:
            print('\nError: Failed to send file. server no response\n')
            prompt(USERNAME)
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
            prompt(USERNAME)

        return 0

    # Using key on secure message
    if str.upper(msg[0:4]) == 'USEK':
        params = str.split(str.strip(msg), ' ', 1)
        key_str = params[1]
        use_key(key_str)
        print(f'\nYou are using key: {key_str}\n')
        prompt(USERNAME)
        return 0

    # Send a secure msg
    if str.upper(msg[0:4]) == 'SECU':
        params = str.split(str.strip(msg), ' ', 2)
        if not (len(params) == 3):
            print('\nError: Invalid parameter, see HELP.\n')
            prompt(USERNAME)
            return 0
        
        # user don't have a key, fail to send secure msg
        if (len(KEY) == 0):
            print('\nError: You don\'t have key now, use USEK.\n')
            prompt(USERNAME)
            return 0

        receiver_name = params[1]
        secure_msg = encrypt(KEY, params[2].encode('utf-8'))
        msg = f'SECU {receiver_name} {secure_msg}'
        client.send(msg.encode('utf-8'))
        return 0


    # Just send data
    client.send(msg.encode('utf-8'))


def analyze_res(res_data,client):
    ''' Analyze a response from server
    '''
    res_data = res_data.decode('utf-8')
    status = res_data[0:3]      # get status code
    res_data = res_data[4:]     # the leaving msg

    # receive a file
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

    # receive a secure msg
    if status == '700':
        params = str.split(res_data, ' ', 1)
        sender_name = params[0]
        encrypted_msg = params[1]

        # try to use a key to decrypt it
        # if client already use a key
        if not (len(KEY) == 0):
            decrypted_msg = decrypt(KEY, encrypted_msg).decode('utf-8')
            res_data = f'\nUser "{sender_name}" send you secure msg: {decrypted_msg}'
        else:
            # otherwise, just display the secure msg
            res_data = f'\nUser "{sender_name}" send you secure msg: {encrypted_msg}'
            res_data += '\nNote: You don\'t have a key now, msg is encrypted.'
    

    # print data in a new line
    print()
    print(res_data)
    print()

    prompt(USERNAME)
    # print ('received', len(res_data), ' bytes')


def use_key(key_str):
    ''' A function to manage keys 
    '''
    global KEY

    KEY = key_str.encode('utf-8')
    return 0


def greet_client(client_socket):
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




############################ Program begin ########################################


# try initiate conn on a socket
try:
    print('Connecting...')
    client.connect((HOST, PORT))
except:
    sys.exit(f'Error: Fail to connect to host: {HOST} on port: {PORT}.')

print(f'Connected successfully.')

# greet client to the server
USERNAME = greet_client(client)


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


