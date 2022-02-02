#!/usr/bin/python

#
# Simulation of the RDT 2.2 protocol described in
# section 3.4.1 of Computer Networking: A Top-Down Approach, Kurose-Ross, 7th edition
#
import sys
from Queue import Queue
from sm import StateMachine
import rdtlib
from rdtlib import rdt_send, udt_send, isACK, iscorrupt, rdt_rcv


#
# Sender
#

lastsndpkt = None     # Holds last sent packet in case it needs to be retransmitted
sent = 0
retrans = 0

# Set up a queue of packets to send
sendbuf = Queue()
for i in 'ABCDEFGHIJ':
    sendbuf.put(i)

# Handle the sender's 'Wait for call from above' states
def sender_wait_above_0():
    global lastsndpkt, sent
    print 'Sender in state WAIT_ABOVE_0'
    # If we have some data to send, send it
    if not sendbuf.empty():
        lastsndpkt = rdt_send(sendbuf.get(), 0)
        sent += 1
        return 'WAIT_ACK_0'
    else:
        return 'S_END'

def sender_wait_above_1():
    global lastsndpkt, sent
    print 'Sender in state WAIT_ABOVE_1'
    # If we have some data to send, send it
    if not sendbuf.empty():
        lastsndpkt = rdt_send(sendbuf.get(), 1)
        sent += 1
        return 'WAIT_ACK_1'
    else:
        return 'S_END'

# Handle the sender's 'Wait for ACK' states
def sender_wait_ack_0():
    global lastsndpkt, retrans
    print 'Sender in state WAIT_ACK_0'
    packet = rdt_rcv()

    if packet == None:    # Timeout!
        print 'Sender: Timeout, retransmitting', lastsndpkt
        udt_send(lastsndpkt)
        retrans += 1
        return 'WAIT_ACK_0'

    if iscorrupt(packet):
        print 'Sender: Corrupt ACK, retransmitting', lastsndpkt
        udt_send(lastsndpkt)
        retrans += 1
        return 'WAIT_ACK_0'

    if isACK(packet, 1):
        print 'Sender: Duplicate ACK, retransmitting', lastsndpkt
        udt_send(lastsndpkt)
        retrans += 1
        return 'WAIT_ACK_0'

    if isACK(packet, 0):
        return 'WAIT_ABOVE_1'

    return 'WAIT_ACK_0'

def sender_wait_ack_1():
    global lastsndpkt, retrans
    print 'Sender in state WAIT_ACK_1'
    packet = rdt_rcv()

    if packet == None:    # Timeout!
        print 'Sender: Timeout, retransmitting', lastsndpkt
        udt_send(lastsndpkt)
        retrans += 1
        return 'WAIT_ACK_1'

    if iscorrupt(packet):
        print 'Sender: Corrupt ACK, retransmitting', lastsndpkt
        udt_send(lastsndpkt)
        retrans += 1
        return 'WAIT_ACK_1'

    if isACK(packet, 0):
        print 'Sender: Duplicate ACK, retransmitting', lastsndpkt
        udt_send(lastsndpkt)
        retrans += 1
        return 'WAIT_ACK_1'

    if isACK(packet, 1):
        return 'WAIT_ABOVE_0'

    return 'WAIT_ACK_1'

def SenderDone():
    print 'Send buffer empty, exiting'
    print 'Sent: ', sent
    print 'Retransmitted: ', retrans

#
# Start two processes, one for the sender, and one for the receiver
# Set up the state machines
#
def start_sender():
    sender = StateMachine('sender')
    sender.add_state('WAIT_ABOVE_0', sender_wait_above_0)
    sender.add_state('WAIT_ABOVE_1', sender_wait_above_1)
    sender.add_state('WAIT_ACK_0', sender_wait_ack_0)
    sender.add_state('WAIT_ACK_1', sender_wait_ack_1)
    sender.add_state('S_END', SenderDone, end_state=1)
    sender.set_initial_state('WAIT_ABOVE_0')
    sender.run()

rdtlib.peer = ('10.0.0.2', 12002)

start_sender()
