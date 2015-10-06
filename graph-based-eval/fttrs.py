import networkx as nx
from generatectmc import colorize_graph, generate_ctmc
from generatectmc import save_graph_drawing, save_ctmc_drawing

from itertools import combinations


def is_faulty(G, switches, slaves, num_necessary_slaves):
    """
    num_necessary_slaves: minimum number of slaves that must be connected to
    each other in graph G for G not to be faulty.
    """
    H = nx.Graph(G)
    num_slaves_cc = {}
    for switch in switches:
        num_slaves_cc[switch] = 0
        if switch in H.nodes_iter():
            cc = nx.node_connected_component(H, switch)
            for vertex in cc:
                if vertex in slaves:
                    num_slaves_cc[switch] = num_slaves_cc[switch] + 1
    return all([num_slaves_cc[switch] < num_necessary_slaves
                for switch in switches])


num_slaves = 2
num_switches = 1
# number of interlinks between each pair of switches
interlink_redundancy = 2
num_required_slaves = 1


class Slave:
    num_slaves = 0

    def __init__(self):
        Slave.num_slaves += 1
        self.index = Slave.num_slaves

    def __repr__(self):
        return 's' + str(self.index)


class Port:
    num_ports = 0

    def __init__(self):
        Port.num_ports += 1
        self.index = Port.num_ports

    def __repr__(self):
        return 'p' + str(self.index)


class Link:
    num_links = 0

    def __init__(self):
        Link.num_links += 1
        self.index = Link.num_links

    def __repr__(self):
        return 'l' + str(self.index)


class Guardian:
    num_guardians = 0

    def __init__(self):
        Guardian.num_guardians += 1
        self.index = Guardian.num_guardians

    def __repr__(self):
        return 'g' + str(self.index)


class Switch:
    num_switches = 0

    def __init__(self):
        Switch.num_switches += 1
        self.index = Switch.num_switches

    def __repr__(self):
        return 'b' + str(self.index)


slaves = [Slave() for i in range(num_slaves)]
ports = []
links = []
guardians = []
switches = [Switch() for i in range(num_switches)]

slave_to_port_edges = []
port_to_slave_edges = []

port_to_link_edges = []
link_to_port_edges = []

link_to_guardian_edges = []
guardian_to_link_edges = []

guardian_to_switch_edges = []
switch_to_guardian_edges = []

switch_to_port_edges = []
port_to_switch_edges = []

for slave in slaves:
    for switch in switches:
        new_slave_port = Port()
        ports.append(new_slave_port)
        slave_to_port_edges.append((slave, new_slave_port))
        port_to_slave_edges.append((new_slave_port, slave))

        new_slavelink = Link()
        links.append(new_slavelink)
        port_to_link_edges.append((new_slave_port, new_slavelink))
        link_to_port_edges.append((new_slavelink, new_slave_port))

        new_guardian = Guardian()
        guardians.append(new_guardian)
        link_to_guardian_edges.append((new_slavelink, new_guardian))
        guardian_to_link_edges.append((new_guardian, new_slavelink))

        guardian_to_switch_edges.append((new_guardian, switch))
        switch_to_guardian_edges.append((switch, new_guardian))

# Create clique of switches interconnected by interlinks
i = 0
for switch1, switch2 in combinations(switches, 2):
    for j in range(interlink_redundancy):
        new_interlink_port = Port()
        ports.append(new_interlink_port)
        switch_to_port_edges.append((switch1, new_interlink_port))
        port_to_switch_edges.append((new_interlink_port, switch1))

        new_interlink = Link()
        links.append(new_interlink)
        port_to_link_edges.append((new_interlink_port, new_interlink))
        link_to_port_edges.append((new_interlink, new_interlink_port))

        new_interlink_port2 = Port()
        ports.append(new_interlink_port2)
        link_to_port_edges.append((new_interlink, new_interlink_port2))
        port_to_link_edges.append((new_interlink_port2, new_interlink))
    i += interlink_redundancy

G = nx.DiGraph()
G.add_edges_from(slave_to_port_edges, coverage=0)
G.add_edges_from(port_to_slave_edges, coverage=0.5)
G.add_edges_from(port_to_link_edges, coverage=0)
G.add_edges_from(link_to_port_edges, coverage=0.5)
G.add_edges_from(link_to_guardian_edges, coverage=0.5)
G.add_edges_from(guardian_to_link_edges, coverage=0)
G.add_edges_from(guardian_to_switch_edges, coverage=0.5)
G.add_edges_from(switch_to_guardian_edges, coverage=0)
G.add_edges_from(switch_to_port_edges, coverage=0)
G.add_edges_from(port_to_switch_edges, coverage=0.5)

class_to_color = {
    tuple(slaves): 'green',
    tuple(switches): 'yellow',
    tuple(links): 'blue',
    tuple(ports): 'red',
    tuple(guardians): 'cyan',
}

colorize_graph(G, class_to_color)

save_graph_drawing(G, 'G.png')

ctmc = generate_ctmc(G, is_faulty, switches, slaves, num_required_slaves)
save_ctmc_drawing(ctmc, 'ctmc.png')

print "Size of state space: {}".format(ctmc.order())

for i in range(5): print
