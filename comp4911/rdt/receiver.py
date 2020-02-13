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

# Handle the receiver's 'Wait for call from below' states
#
# There are three cases to handle for each of these:
# 1. Packet is corrupt
# 2. Packet is out-of-sequence
# 3. Packet is OK
def receiver_wait_below_0():
    print 'Receiver in state WAIT_BELOW_0'
    packet = rdt_rcv()

    if iscorrupt(packet):
         packet = make_pkt(type=ACK, seq=1)
         print 'Receiver: corrupt packet, sending ACK1', packet
         udt_send(packet)
         return 'WAIT_BELOW_0'
    else:
         if hasSeq(packet, 1):
             packet = make_pkt(type=ACK, seq=1)
             print 'Receiver: wrong seq num, expected 0, sending ACK1', packet
             udt_send(packet)
             return 'WAIT_BELOW_0'
         else:
             # OK, transition to waiting for packet with seq=1
             data = extract(packet)
             deliver_data(data)
             packet = make_pkt(type=ACK, seq=0)
             print 'Receiver: packet OK, sending ACK0', packet
             udt_send(packet)
             return 'WAIT_BELOW_1'

def receiver_wait_below_1():
    print 'Receiver in state WAIT_BELOW_1'
    packet = rdt_rcv()

    if iscorrupt(packet):
         packet = make_pkt(type=ACK, seq=0)
         print 'Receiver: corrupt packet, sending ACK0', packet
         udt_send(packet)
         return 'WAIT_BELOW_1'
    else:
         if hasSeq(packet, 0):
             packet = make_pkt(type=ACK, seq=0)
             print 'Receiver: wrong seq num, expected 1, sending ACK0', packet
             udt_send(packet)
             return 'WAIT_BELOW_1'
         else:
             # OK, transition to waiting for packet with seq=0
             data = extract(packet)
             deliver_data(data)
             packet = make_pkt(type=ACK, seq=1)
             print 'Receiver: packet OK, sending ACK1', packet
             udt_send(packet)
             return 'WAIT_BELOW_0'


def ReceiverDone():
    pass

#
# Set up the state machines
#

def start_receiver():
    receiver = StateMachine('receiver')
    receiver.add_state('WAIT_BELOW_0', receiver_wait_below_0)
    receiver.add_state('WAIT_BELOW_1', receiver_wait_below_1)
    receiver.add_state('R_END', ReceiverDone, end_state=1)
    receiver.set_initial_state('WAIT_BELOW_0')
    receiver.run()

rdtlib.peer = ('10.0.0.1', 12002)
start_receiver()
