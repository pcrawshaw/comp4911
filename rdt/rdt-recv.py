#!/usr/bin/python3

# "RDT over UDP" protocol receiver

# NOTE: This is incomplete!
#       What happens when you run the sender a second time without restarting the receiver?
#       How can you fix this?

# See rdt.py for the packet format

from socket import *
from rdt import *
import json

PORT = 12000

# Listen for UDP datagrams on port# PORT
# SO_REUSEADDR eliminates "port already in use" errors
recvSock = socket(AF_INET, SOCK_DGRAM)
recvSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
recvSock.bind(('', PORT))

# Initialize receiver state
expectedseqnum = 1
sndpkt = make_ack_pkt(0)

# Run forever, processing received UDP datagrams
while True:

    # Receive a packet. rdt_recv() returns a Python dict,
    # as defined in 'packet format' in rdt.py
    packet, peer = rdt_rcv(recvSock)
    print('\nReceived ' + str(packet))

    # if packet is not corrupt and has expected seqnum
    #     extract data and deliver to application layer
    #     send ACK for expectedseqnum
    # else
    #     send last ack packet
    if notcorrupt(packet) and hasseqnum(packet, expectedseqnum):

        # 'deliver to application  layer' means print it on the screen
        data = extract_data(packet)
        print('DELIVERED TO APP: ' + str(data))

        # Send an ACK for this newly-arrived packet
        sndpkt = make_ack_pkt(expectedseqnum)
        expectedseqnum +=1
        udt_send(recvSock, sndpkt, peer)
        print('Sending ' + str(sndpkt))
    else:
        # Send the last ACK
        print("RECEIVED CORRUPT PACKET OR WRONG SEQNUM!")
        udt_send(recvSock, sndpkt, peer)
        print('Sending ' + str(sndpkt))
