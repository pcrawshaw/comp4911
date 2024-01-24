# Imports
import sys
from socket import socket, AF_INET, SOCK_STREAM
# See: https://docs.python.org/3/library/socket.html

# Get host:port to connect to from command line
# If anything goes wrong, assume bad args and print usage
try:
    args = sys.argv[1].split(':')
    serverIP = args[0]
    serverPort = int(args[1])  # port must be int
except:
    print ('Usage: TCPClient.py host:port')
    sys.exit(1)

# Create a socket
clientSocket = socket(AF_INET, SOCK_STREAM)

# Open TCP connection to server
clientSocket.connect((serverIP, serverPort))

# Read string from keyboard
sentence = input('Input lowercase sentence: ')

# Encode string as bytes and send to server
# Note that we don't need to specify the host and port here, as with UDP
# since we have an open connection to the server (using our socket)
clientSocket.send(sentence.encode())

# Read server's response
# Also no reference to host and port
modifiedSentence = clientSocket.recv(1024)

# Decode bytes to string and display
print ('From Server: ' + modifiedSentence.decode())

# Close the socket
clientSocket.close()

