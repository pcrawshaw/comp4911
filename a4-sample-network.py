#!/usr/bin/python

# Sample network created using Mininet Python API

# Initial code generated with Miniedit (~mininet/mininet/examples/miniedit.py)

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():
    # Create a Mininet controller with no topology
    net = Mininet(controller=Controller, topo=None, build=False, ipBase='0.0.0.0/0')
    c0 = net.addController('c0')

    # Add two routers
    # NOTE: A router is a Mininet host with multiple interaces and IP forwarding enabled.
    #       We add the IP addresses to the routers below, after the network is started.
    info( '*** Add routers\n')
    r1 = net.addHost('r1', cls=Node, ip='0.0.0.0')
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')
    r2 = net.addHost('r2', cls=Node, ip='0.0.0.0')
    r2.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Add hosts, one on each of the 10.0.*.0/24 subnets
    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.1.1/24', defaultRoute='via 10.0.1.254')
    h2 = net.addHost('h2', cls=Host, ip='10.0.2.1/24', defaultRoute='via 10.0.2.254')

    # Add Links between hosts and routers
    # NOTE: *** The order that links are added determines the interface names ***
    # The first interace added to r1 will be r1-eth0, the second will be r1-eth1, etc.
    info( '*** Add links\n')
    net.addLink(h1, r1)
    net.addLink(r1, r2)
    net.addLink(r2, h2)

    # Start the network
    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    c0.start()

    # Set IP addresses on router interfaces
    info( '*** Post configure switches and hosts\n')
    r1.setIP('10.0.1.254/24', intf='r1-eth0')
    r1.setIP('192.168.1.1/24', intf='r1-eth1')
    r2.setIP('192.168.1.2/24', intf='r2-eth0')
    r2.setIP('10.0.2.254/24', intf='r2-eth1')

    # Add routes on r1 and r2
    info( '*** Adding routes on r1 and r2\n')
    r1.cmd('ip route add 10.0.2.0/24 via 192.168.1.2 dev r1-eth1')
    r2.cmd('ip route add 10.0.1.0/24 via 192.168.1.1 dev r2-eth0')

    # Run CLI
    CLI(net)

    # Shutdown the topology when user exits the CLI
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
