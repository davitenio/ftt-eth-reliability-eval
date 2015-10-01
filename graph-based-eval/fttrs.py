import networkx as nx
from generatectmc import colorize_graph, generate_ctmc
from generatectmc import save_graph_drawing, save_ctmc_drawing

from itertools import combinations


def is_faulty(G, switches, slaves, num_necessary_slaves):
    """
    num_necessary_slaves: minimum number of slaves that must be connected to
    each other in graph G for G not to be faulty.
    """
    num_slaves_cc = {}
    for switch in switches:
        num_slaves_cc[switch] = 0
        if switch in G.nodes_iter():
            cc = nx.node_connected_component(G, switch)
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


class Switch:
    num_switches = 0

    def __init__(self):
        Switch.num_switches += 1
        self.index = Switch.num_switches

    def __repr__(self):
        return 'b' + str(self.index)


E = []
slaves = [Slave() for i in range(num_slaves)]
ports = []
links = []
switches = [Switch() for i in range(num_switches)]

for slave in slaves:
    for switch in switches:
        new_slave_port = Port()
        ports.append(new_slave_port)
        E.append((slave, new_slave_port))
        new_slavelink = Link()
        links.append(new_slavelink)
        E.append((new_slave_port, new_slavelink))
        new_switch_port = Port()
        ports.append(new_switch_port)
        E.append((new_slavelink, new_switch_port))
        E.append((new_switch_port, switch))

# Create clique of switches interconnected by interlinks
i = 0
for switch1, switch2 in combinations(switches, 2):
    for j in range(interlink_redundancy):
        new_interlink_port = Port()
        ports.append(new_interlink_port)
        E.append((switch1, new_interlink_port))
        new_interlink = Link()
        links.append(new_interlink)
        E.append((new_interlink_port, new_interlink))
        new_interlink_port2 = Port()
        ports.append(new_interlink_port2)
        E.append((new_interlink, new_interlink_port2))
        E.append((new_interlink_port2, switch2))
    i += interlink_redundancy

G = nx.Graph()
G.add_edges_from(E)


class_to_color = {
    tuple(slaves): 'green',
    tuple(switches): 'yellow',
    tuple(links): 'blue',
    tuple(ports): 'red',
}

colorize_graph(G, class_to_color)

save_graph_drawing(G, 'G.png')

ctmc = generate_ctmc(G, is_faulty, switches, slaves, num_required_slaves)
save_ctmc_drawing(ctmc, 'ctmc.png')

print "Size of state space: {}".format(ctmc.order())

for i in range(5): print
