# Functions useful for simulating reliable data transfer protocols
# See Computer Networking: A Top-Down Approach, Kurose-Ross, 6th edition, section 3.4

#from multiprocessing import Process
import time, random
from copy import deepcopy
import json
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR

from sm import StateMachine # in sm.py

# Adjust these
PROBABILITY_OF_CORRUPTION = 0.0
PROBABILITY_OF_PACKET_LOSS = 0.0
TIME_TO_SEND_PACKET = 0.01
SENDER_TIMEOUT = 2
UDT_PORT = 12002
peer = ('', UDT_PORT)


# We have three types of packets
DATA, ACK, NAK = 0, 1, 2

# Our packet format looks like this:
# [[checksum, sequence-number, packet-type], data]
# i.e.: a two-element list where the first element is a three-lement list
# so packet[0][0] is the checksum, packet[0][1] is the sequence number, and so on

# Use this to simulate a communications link
recvSock = socket(AF_INET, SOCK_DGRAM)
recvSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
recvSock.bind(('', UDT_PORT))


# Utility functions

# 16-bit one's complement checksum checksum
def checksum(packet):
    [[ck, seq, type], data] = packet

    # Treat these as 16-bit integers
    sum = ck
    sum += seq
    sum += type

    # Make 16 bit words out of every two adjacent 8 bit words in the packet
    # and sum them
    for i in range(0, len(data), 2):
        if i + 1 >= len(data):       # Last byte when len(data) is odd
            sum += ord(data[i]) & 0xFF
        else:
            w = ((ord(data[i]) << 8) & 0xFF00) + (ord(data[i+1]) & 0xFF)
            sum += w

    # Take only 16 bits out of the 32 bit sum and add up the carries, 
    # then add them to the sum
    while (sum >> 16) > 0:
        sum = (sum & 0xFFFF) + (sum >> 16)

    # One's complement the result
    return ~sum & 0xFFFF

# Returns True if the packet is corrupt
# When we verify the checksum at the receiver, we expect to get 0.
def iscorrupt(packet):
    ck = checksum(packet)
    return ck != 0

# Create a packet (see packet format, above)
# Note that the checksum is taken using 0 in the checksum field
# then we fill in the checksum value
def make_pkt(data='', seq=0, type=DATA):
    packet = ([0, seq, type], data)
    ck = checksum(packet)
    packet[0][0] = ck
    return packet

# Sender functions

# Called by higher layer to send a packet
def rdt_send(data, seq):
    packet = make_pkt(data=data, seq=seq)
    print 'Sender: sending', packet
    udt_send(packet)
    return packet  # also return the packet we sent so we can buffer it

# Unreliable send() function.  Packets may be corrupted or lost
def udt_send(packet):
    newpkt = deepcopy(packet)
    # Maybe corrupt the packet
    if random.random() < PROBABILITY_OF_CORRUPTION:
        newpkt = ([23432, 65546, 67887], 'Blah blah blah!')
        print 'PACKET WILL BE CORRUPTED:', packet

    # Pretend it takes some time to transmit
    time.sleep(TIME_TO_SEND_PACKET)

    # Maybe drop a packet (including corrupt ones)
    if random.random() < PROBABILITY_OF_PACKET_LOSS:
        print 'PACKET WILL BE LOST:', packet
        return

    # Send the packet with UDP. Serialize the python object with json
    s = json.dumps(newpkt)
    sock = socket(AF_INET, SOCK_DGRAM)
    print "Sending", newpkt, "to", peer
    sock.sendto(s, peer)

# Return True if the packet is an ACK
def isACK(packet, acknum=0):
    header, data = packet
    checksum, seq, type = header
    return type == ACK and seq == acknum

# Return True if the packet is a NAK
def isNAK(packet, acknum=0):
    header, data = packet
    checksum, seq, type = header
    return type == NAK and seq == acknum

# Check for sequence number match
def hasSeq(packet, seqnum):
    header, data = packet
    checksum, seq, type = header
    return seq == seqnum

# Receiver functions
# Get a packet from the comm channel
def rdt_rcv(timeout=None):
    # This will block for up to 'timeout' sec until there is something in the 
    # queue to get().  None means wait for ever.
    try:
        recvSock.settimeout(timeout)  # if None, no timeout
        data, sender = recvSock.recvfrom(2048)
        packet = json.loads(data)
        print "Received", packet, "from", sender
    except:
        return None
    return packet

# Extract the data field from a packet and return it
def extract(packet):
    header, data = packet
    return data

# Deliver data to the application
def deliver_data(data):
    print 'Receiver delivers to app:', data
