#!/usr/bin/python

# The "how many subnets" example with OSPF
# We use OSPF from the BIRD routing daemon (https://bird.network.cz/)

# The three routers (r1, r3, and r3) all run the OSPF protocol:
#   they exchange link state info and then independently build
#   their forwarding tables

# You can see what happens in the log file for each router (r1.log, etc.)

# NOTE: To run this you must first install BIRD:
#   sudo apt install bird

# We don't want to run BIRD on the Mininet VM directly, so stop and disable it:
#   sudo systemctl stop bird
#   sudo systemctl disable bird
#   sudo systemctl stop bird6
#   sudo systemctl disable bird6

# Confirm installation with bird --version

# Run with sudo -E python hms-bird-ospf.py

# Try the bird shell:
#
#   sudo birdc -s r1.ctl
#
# where r1.ctl is the control file for router r1, and so on
#
# Try some commands:
#
#   bird> show interfaces summary
#   bird> show route
#   bird> show ospf
#   bird> show ospf interface
#   bird> show ospf neighbors
#   bird> show ospf lsadb
#   bird> show ospf topology


import os
from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import Node, Host
from mininet.topo import Topo


class Router(Node):
    """A Node with IP forwarding enabled and the BIRD routing daemon running"""

    def config(self, **params):
        super(Router, self).config(**params)

        # Enable forwarding on the router
        self.cmd('sysctl net.ipv4.ip_forward=1')

        # Startup BIRD
        self.cmd('/usr/sbin/bird -c {0}.conf -s {0}.ctl'.format(self.name))

    def terminate(self):
        # Disable forwarding
        self.cmd('sysctl net.ipv4.ip_forward=0')

        # Shutdown BIRD
        self.cmd('/usr/sbin/birdc -s {0}.ctl down'.format(self.name))

        super(Router, self).terminate()


class Topology(Topo):

    # Build the network
    def build(self, *args, **params):
        # Create three routers
        r1 = self.addNode('r1', cls=Router, ip='10.1.9.2/24')
        r2 = self.addNode('r2', cls=Router, ip='10.1.9.1/24')
        r3 = self.addNode('r3', cls=Router, ip='10.1.7.1/24')

        # Add links between routers
        self.addLink(r1, r2,
                     intfName1='r1-eth3', params1={'ip': '10.1.9.2/24'},
                     intfName2='r2-eth1', params2={'ip': '10.1.9.1/24'})
        self.addLink(r1, r3,
                     intfName1='r1-eth2', params1={'ip': '10.1.7.2/24'},
                     intfName2='r3-eth1', params2={'ip': '10.1.7.1/24'})
        self.addLink(r2, r3,
                     intfName1='r2-eth2', params1={'ip': '10.1.8.1/24'},
                     intfName2='r3-eth3', params2={'ip': '10.1.8.2/24'})

        # Create three hosts
        h1 = self.addHost('h1', cls=Host, ip='10.1.1.1/24', defaultRoute='via 10.1.1.3')
        h2 = self.addHost('h2', cls=Host, ip='10.1.2.1/24', defaultRoute='via 10.1.2.6')
        h3 = self.addHost('h3', cls=Host, ip='10.1.3.1/24', defaultRoute='via 10.1.3.27')

        # Add links between hosts and routers
        self.addLink(h1, r1,
                     intfName1='h1-eth1', params1={'ip': '10.1.1.1/24'},
                     intfName2='r1-eth1', params2={'ip': '10.1.1.3/24'})
        self.addLink(h2, r2,
                     intfName1='h2-eth1', params1={'ip': '10.1.2.1/24'},
                     intfName2='r2-eth3', params2={'ip': '10.1.2.6/24'})
        self.addLink(h3, r3,
                     intfName1='h2-eth1', params1={'ip': '10.1.3.1/24'},
                     intfName2='r3-eth2', params2={'ip': '10.1.3.27/24'})


def run():
    """OSPF Test Network"""
    topology = Topology()
    net = Mininet(topo=topology, controller=None)
    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
