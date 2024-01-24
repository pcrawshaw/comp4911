# Simple UDP server

# Imports from the socket module: https://docs.python.org/3/library/socket.html
from socket import socket, AF_INET, SOCK_DGRAM

serverPort = 12000

# Create a UDP socket
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Bind socket to local (address, port)
# '' means "all local addresses"
serverSocket.bind(('', serverPort))

# Loop forever to wait for incoming datagrams
print ('Waiting for datagrams on port {}, Ctrl+C to exit'.format(serverPort))
while True:
    # Receive a datagram, storing remote adress, port
    message, clientAddress = serverSocket.recvfrom(1024)
    print('Received a datagram from {}: {}'.format(clientAddress, message))

    # Decode the bytes into a string and convert to uppercase
    modifiedMsg = message.decode().upper()

    # Send it back to the client in a datagram
    serverSocket.sendto(modifiedMsg.encode(), clientAddress)

    # Continue the loop, ready to receive a new datagram
