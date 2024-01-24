# Simple TCP server

# Imports from the socket module: https://docs.python.org/3/library/socket.html
from socket import socket, AF_INET, SOCK_STREAM

# We will listen for client connections on port 12000
serverPort = 12000

# Create a TCP socket
serverSocket = socket(AF_INET, SOCK_STREAM)

# Bind socket to local (address, port) and listen for incoming connections
# '' means "all local addresses"
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

# Loop forever to process incoming connections
print('Listening on TCP port {}, Ctrl+C to exit'.format(serverPort))
while True:
     # Accept a new TCP connection, allocating a new socket
     connectionSocket, addr = serverSocket.accept()
     print('Connection from' + str(addr))

     # IMPORTANT NOTE:
     # At this point we have an open full-duplex TCP connection
     # with the client as the other endpoint. Compare and contrast 
     # this with the UDP example

     # Read bytes from the client, decode into string
     sentence = connectionSocket.recv(1024).decode()
     print('Received: ' + sentence)

     # Uppercase the received text
     capitalizedSentence = sentence.upper()

     # Send it back to the client on the still open TCP connection
     print('Sending: ' + capitalizedSentence)
     connectionSocket.send(capitalizedSentence.encode())

     # Close the connection
     connectionSocket.close()

     # Continue the loop, ready to accept() a new connection
