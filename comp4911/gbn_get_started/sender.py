#!/usr/bin/python

# sender.py
# Go-Back-N simulation based on the RDT 2.2 protocol described in
# section 3.4.1 of Computer Networking: A Top-Down Approach, Kurose-Ross, 7th edition
#
import sys
from Queue import Queue
from sm import StateMachine
import rdtlib
from rdtlib import rdt_send, udt_send, isACK, iscorrupt, rdt_rcv

# Globals
lastsndpkt = None # Holds last sent packet in case it needs to be retransmitted
nextseqnum = 0
base = 0
sent = 0
retrans = 0

# Set up a queue of packets to send
sendbuf = Queue()
for i in 'ABCDEFGHIJ':
    sendbuf.put(i)

# Handle the sender's 'Wait for call from above' state
def sender_wait_above():
    global lastsndpkt, nextseqnum, sent

    print 'Sender in state WAIT_ABOVE'
    # If we have some data to send, send it using nextseqnum
    if not sendbuf.empty():
        lastsndpkt = rdt_send(sendbuf.get(), nextseqnum)
        sent += 1
        # Advance nextseqnum for next packet that will be sent
        nextseqnum += 1
        return 'WAIT_ACK'     # Wait for the ACK
    else:
        return 'S_END'        # Terminate state machine

# Handle the sender's 'Wait for ACK' state
def sender_wait_ack():
    global lastsndpkt, retrans, base
    print 'Sender in state WAIT_ACK'

    # Wait to receive an ACK packet
    packet = rdt_rcv(timeout=None)

    # TODO: These three error condtions could be collapsed into a single case
    if packet == None:    # Timeout!
        print 'Sender: Timeout, retransmitting', lastsndpkt
        udt_send(lastsndpkt)
        retrans += 1
        return 'WAIT_ACK'

    if iscorrupt(packet):
        print 'Sender: Corrupt ACK, retransmitting', lastsndpkt
        udt_send(lastsndpkt)
        retrans += 1
        return 'WAIT_ACK'

    if not isACK(packet, base):
        print 'Sender: Duplicate ACK, retransmitting', lastsndpkt
        udt_send(lastsndpkt)
        retrans += 1
        return 'WAIT_ACK'

    # Expected ACK is received, advance base of sender window by 1
    if isACK(packet, base):
        base += 1
        return 'WAIT_ABOVE'

    # Default case, keep waiting for an ACK
    return 'WAIT_ACK'


def SenderDone():
    print 'Send buffer empty, exiting'
    print 'Sent: ', sent
    print 'Retransmitted: ', retrans

#
# Set up the state machine
#
def start_sender():
    sender = StateMachine('sender')
    sender.add_state('WAIT_ABOVE', sender_wait_above)
    sender.add_state('WAIT_ACK', sender_wait_ack)
    sender.add_state('S_END', SenderDone, end_state=1)
    sender.set_initial_state('WAIT_ABOVE')
    sender.run()

rdtlib.peer = ('10.0.0.2', 12002)

start_sender()
