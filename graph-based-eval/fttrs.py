import networkx as nx
from generatectmc import colorize_graph, generate_ctmc
from generatectmc import save_graph_drawing, save_ctmc_drawing

from itertools import combinations


def is_correct(G, slaves, num_necessary_slaves):
    """
    num_necessary_slaves: minimum number of slaves that must be connected to
    each other in graph G for G not to be faulty.
    """
    H = nx.Graph(G)
    num_non_faulty_cc = 0
    for cc_vertices in nx.connected_components(H):
        num_slaves_in_cc = len(set(cc_vertices) & set(slaves))
        if num_slaves_in_cc >= num_necessary_slaves:
            # Check that the slaves are not a vertex cut in the connected
            # component.
            H2 = nx.Graph(H)
            H2.remove_nodes_from(slaves)
            # We check that order > 0 because nx.is_connected() is not defined
            # for the null graph.
            if H2.order() > 0 and nx.is_connected(H2):
                num_non_faulty_cc += 1

    # G is correct (non-faulty) if it has exactly 1 non-faulty connected
    # component. Having more than 1 correct component is considered a failure
    # because we assume that if the system is split into more than one
    # functioning subsystem, this is a failure.
    if num_non_faulty_cc == 1:
        return True
    else:
        return False


def is_faulty(G, slaves, num_necessary_slaves):
    return not is_correct(G, slaves, num_necessary_slaves)


num_slaves = 2
num_switches = 1
# number of interlinks between each pair of switches
interlink_redundancy = 1
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
        switch_to_port_edges.append((switch2, new_interlink_port2))
        port_to_switch_edges.append((new_interlink_port2, switch2))
    i += interlink_redundancy

G = nx.DiGraph()
G.add_edges_from(
    slave_to_port_edges,
    failure_mode_to_coverage={'crash': 0, 'byzantine': 0})
G.add_edges_from(
    port_to_slave_edges,
    failure_mode_to_coverage={'crash': 1, 'byzantine': 0})
G.add_edges_from(
    port_to_link_edges,
    failure_mode_to_coverage={'crash': 0, 'byzantine': 0})
G.add_edges_from(
    link_to_port_edges,
    failure_mode_to_coverage={'crash': 1, 'byzantine': 0.1})
G.add_edges_from(
    link_to_guardian_edges,
    failure_mode_to_coverage={'crash': 1, 'byzantine': 0.8})
G.add_edges_from(
    guardian_to_link_edges,
    failure_mode_to_coverage={'crash': 0, 'byzantine': 0})
G.add_edges_from(
    guardian_to_switch_edges,
    failure_mode_to_coverage={'crash': 1, 'byzantine': 0})
G.add_edges_from(
    switch_to_guardian_edges,
    failure_mode_to_coverage={'crash': 0, 'byzantine': 0})
G.add_edges_from(
    switch_to_port_edges,
    failure_mode_to_coverage={'crash': 0, 'byzantine': 0})
G.add_edges_from(
    port_to_switch_edges,
    failure_mode_to_coverage={'crash': 1, 'byzantine': 0})

nx.set_node_attributes(
    G, 'failure_mode_to_rate',
    {s: {'crash': 0.01, 'byzantine': 0.001} for s in slaves})
nx.set_node_attributes(
    G, 'failure_mode_to_rate',
    {p: {'crash': 0.01, 'byzantine': 0.001} for p in ports})
nx.set_node_attributes(
    G, 'failure_mode_to_rate',
    {l: {'crash': 0.01, 'byzantine': 0.001} for l in links})
nx.set_node_attributes(
    G, 'failure_mode_to_rate',
    {g: {'crash': 0.01, 'byzantine': 0.001} for g in guardians})
nx.set_node_attributes(
    G, 'failure_mode_to_rate',
    {b: {'crash': 0.01, 'byzantine': 0.001} for b in switches})


class_to_color = {
    tuple(slaves): 'green',
    tuple(switches): 'yellow',
    tuple(links): 'blue',
    tuple(ports): 'red',
    tuple(guardians): 'cyan',
}

colorize_graph(G, class_to_color)

print G.nodes(data=True)
save_graph_drawing(G, 'G.png')

ctmc = generate_ctmc(G, is_faulty, slaves, num_required_slaves)
save_ctmc_drawing(ctmc, 'ctmc.png')


E = []
for u, v in ctmc.edges_iter():
    E.append(
        (str(sorted([str(w) for w in u.nodes()])),
         str(sorted([str(w) for w in v.nodes()])),
         {'Label': str(sorted(ctmc[u][v]['failed_element']))}))

ctmc_with_strings = nx.DiGraph()
ctmc_with_strings.add_edges_from(E)

nx.write_graphml(ctmc_with_strings, 'ctmc.graphml')

print "Size of state space: {}".format(ctmc.order())

print
