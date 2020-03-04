#!/usr/bin/python

#
# Simulation of the RDT 2.2 protocol described in
# section 3.4.1 of Computer Networking: A Top-Down Approach, Kurose-Ross, 7th edition
#
import sys
from sm import StateMachine
import rdtlib
from rdtlib import udt_send, rdt_send, rdt_rcv, deliver_data, make_pkt, extract, iscorrupt, hasSeq, ACK

#
# Receiver
#

expectedseqnum = 0


# Handle the receiver's 'Wait for call from below' states
#
# There are three cases to handle for each of these:
# 1. Packet is corrupt
# 2. Packet is out-of-sequence
# 3. Packet is OK
def receiver_wait_below():
    global expectedseqnum

    print 'Receiver in state WAIT_BELOW'
    packet = rdt_rcv()

    # We have a good packet with the right seqnum, so deliver data
    # to app layer and send an acknowledgement
    if not iscorrupt(packet) and hasSeq(packet, expectedseqnum):
         data = extract(packet)
         deliver_data(data)

         packet = make_pkt(type=ACK, seq=expectedseqnum)

         expectedseqnum += 1
         expectedseqnum %= 2
         print 'Receiver: packet OK, sending ACK', packet
    else:
         packet = make_pkt(type=ACK, seq=expectedseqnum)
         print 'Receiver: bad packet, sending ACK', packet

    udt_send(packet)

    return 'WAIT_BELOW'


def ReceiverDone():
    pass

#
# Set up the state machines
#

def start_receiver():
    receiver = StateMachine('receiver')
    receiver.add_state('WAIT_BELOW', receiver_wait_below)
    receiver.add_state('R_END', ReceiverDone, end_state=1)
    receiver.set_initial_state('WAIT_BELOW')
    receiver.run()

rdtlib.peer = ('10.0.0.1', 12002)
start_receiver()
