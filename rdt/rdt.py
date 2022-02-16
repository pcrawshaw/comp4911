import json

"""
Support library for "RDT over UDP" protocol

In-memory packet format is a Python dict:
{ seq: 1, type: 'DATA', checksum: 12345, data: 'asdf' }

On-the-wire packet format is JSON:
{ "seq": 1, "type": "DATA", "checksum": 12345, "data": "asdf" }

'type' is either 'DATA' or 'ACK'
"""

def make_data_pkt(seq, data):
    """
    Create and return data packet

    Parameters:
        seq (int):     sequence number
        data (string): data to send

    Returns:
        dict representation of a packet
    """
    packet = { 'seq': seq, 'type': 'DATA', 'checksum': 0, 'data': data }
    packet['checksum'] = checksum(packet)
    return packet

def make_ack_pkt(seq):
    """
    Create an acknowledgement packet

    Parameters:
        seq (int):     sequence number

    Returns:
        dict representation of a packet

    """
    # Note that we first set the checksum field to 0 before calculating it
    packet = { 'seq': seq, 'type': 'ACK', 'checksum': 0, 'data': '' }
    packet['checksum'] = checksum(packet)
    return packet

def udt_send(sock, sndpkt, dest):
    """
    Send a 'packet' to an (address, port) destination using UDP

    Parameters:
        sock (socket):  a UDP socket
        sndpkt: (dict): as specified in the 'packet format'

    Returns:
        number of bytes sent
    """
    # Convert to JSON, encode as bytes and send in a UDP datagram
    s = json.dumps(sndpkt)
    return sock.sendto(s.encode(), dest)

def rdt_rcv(sock):
    """
    Receive a packet in a UDP datagram.
    Parameters:
       sock (socket): a UDP socket

    Returns: a dict, as specified in the 'packet format'
             sender (address, port)
    """
    # recvfrom() will return a byte array
    packet, sender = sock.recvfrom(2048)
    # encode as text, which should be in JSON format, then convert to a dict
    return json.loads(packet.decode()), sender

def notcorrupt(packet):
    """
    Returns True if the packet is corrupt

    Parameters:
        packet (dict): as specified in the 'packet format'

    """
    # When we verify the checksum at the receiver, we expect to get 0.
    ck = checksum(packet)
    return ck == 0

def hasseqnum(packet, seqnum):
    """
    Check for sequence number match

    Parameters:
        seqnum (int):  a sequence number
        packet (dict): as specified in the 'packet format'
    """
    return packet['seq'] == seqnum

def extract_data(packet):
    """
    Extract the data field from a packet and return it

    Parameters:
        packet (dict): as specified in the 'packet format'
    """
    return packet['data']

def getacknum(packet):
    """
    Extract the sequence number field from a packet and return it

    Parameters:
        packet (dict): as specified in the 'packet format'
    """
    return packet['seq']

def checksum(packet):
    """
    16-bit one's complement checksum

    Parameters:
        packet (dict): as specified in the 'packet format'

    Returns:
        checksum (integer)
    """
    ck = packet['checksum']
    seq = packet['seq']
    type = packet['type']
    data = packet['data']

    # Treat these as 16-bit integers
    sum = ck
    sum += seq

    # Concatenate type and data
    data = type + data

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
