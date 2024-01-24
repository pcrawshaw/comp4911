# Simple UDP Client

# Imports
import sys
from socket import socket, AF_INET, SOCK_DGRAM
# See: https://docs.python.org/3/library/socket.html

# Get host:port to connect to from command line
# If anything goes wrong, assume bad args and print usage
try:
    args = sys.argv[1].split(':')
    serverIP = args[0]
    serverPort = int(args[1])  # port must be int
except:
    print ('Usage: UDPClient.py host:port')
    sys.exit(1)

# Create a socket
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Read string from keyboard
message = input('Input lowercase sentence: ')

# Encode string as bytes, and send as a datagram to server
# Note that we specify the host,port (compare with TCP example)
# Unlike the TCP example, we don't maintain an open connection to the server
# Recall that UDP's service model is (among other things) 'connectionless'
clientSocket.sendto(message.encode(), (serverIP, serverPort))

# Read server's response, storing address,port in a variable
modifiedMessage, serverAddress = clientSocket.recvfrom(1024)

# Decode bytes into string and display
print (modifiedMessage.decode())

# Close the socket
clientSocket.close()

