from socket import *

serverIP = '10.0.0.2'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
message = raw_input('Input lowercase sentence:')
clientSocket.sendto(message.encode(), 
                      (serverIP, serverPort))
modifiedMessage, serverAddress = 
           clientSocket.recvfrom(2048)
print (modifiedMessage.decode())
clientSocket.close()

