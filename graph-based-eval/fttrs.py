import networkx as nx
from generatectmc import colorize_graph, generate_ctmc
from generatectmc import save_graph_drawing, save_ctmc_drawing

from itertools import cycle, combinations


def is_faulty(G, switch_regions, slave_regions, num_necessary_slaves):
    """
    num_necessary_slaves: minimum number of slaves that must be connected to
    each other in graph G for G not to be faulty.
    """
    num_slave_regions_cc = {}
    for switch_reg in switch_regions:
        num_slave_regions_cc[switch_reg] = 0
        if switch_reg in G.nodes_iter():
            cc = nx.node_connected_component(G, switch_reg)
            for vertex in cc:
                if vertex in slave_regions:
                    num_slave_regions_cc[switch_reg] = (
                        num_slave_regions_cc[switch_reg] + 1)
    return all([num_slave_regions_cc[switch_reg] < num_necessary_slaves
                for switch_reg in switch_regions])


num_slave_regions = 1
num_switch_regions = 2
# number of interlinks between each pair of switches
interlink_redundancy = 2
num_required_slaves = 1


num_link_regions = num_switch_regions * num_slave_regions
# A clique K_n has n choose 2 = n * (n-1)/2 edges
num_interlink_regions = (interlink_redundancy * num_switch_regions *
    (num_switch_regions - 1)/2)


slave_regions = tuple(['s' + str(i) for i in range(num_slave_regions)])
slavelink_regions = tuple(['l' + str(i) for i in range(num_link_regions)])
switch_regions = tuple(['b' + str(i) for i in range(num_switch_regions)])
interlink_regions = tuple(['i' + str(i) for i in range(num_interlink_regions)])

link_regions = slavelink_regions + interlink_regions

def cycle_zip(list1, list2):
    if len(list1) > len(list2):
        return zip(list1, cycle(list2))
    elif len(list1) < len(list2):
        return zip(cycle(list1), list2)
    else:
        return zip(list1, list2)


E = cycle_zip(slavelink_regions, slave_regions)

for slave_reg in slave_regions:
    slavelink_regions_of_slave = [a for (a, b) in E if b == slave_reg]
    E.extend(cycle_zip(slavelink_regions_of_slave, switch_regions))

# Create clique of switch regions interconnected by interlink_regions
i = 0
for switch1, switch2 in combinations(switch_regions, 2):
    for j in range(interlink_redundancy):
        E.append((switch1, interlink_regions[i+j]))
        E.append((switch2, interlink_regions[i+j]))
    i += interlink_redundancy

G = nx.Graph()
G.add_edges_from(E)

class_to_color = {
    slave_regions: 'green',
    switch_regions: 'yellow',
    link_regions: 'blue',
}

colorize_graph(G, class_to_color)

save_graph_drawing(G, 'G.png')

ctmc = generate_ctmc(
    G, is_faulty, switch_regions, slave_regions, num_required_slaves)
save_ctmc_drawing(ctmc, 'ctmc.png')

print "Size of state space: {}".format(ctmc.order())

for i in range(5): print
