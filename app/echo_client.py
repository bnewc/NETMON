# Citation for the following program:
# Date: 01/28/2024
# Written with reference to:
# Source URL: https://docs.python.org/3/howto/sockets.html
# Source URL: https://docs.python.org/3/library/socket.html

import socket

# Set up client socket
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server socket
with client_sock:
    client_sock.connect(('localhost', 45446))

    # Until user enters stop, send any input to server and print its response
    while True:
        msg = input()
        if msg.lower() == 'stop':
            break
        client_sock.sendall(msg.encode())
        response = client_sock.recv(1024)
        print(response.decode())
