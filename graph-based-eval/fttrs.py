import networkx as nx
from generatectmc import *

from itertools import cycle, combinations

num_slaves = 2
num_switches = 2
# number of interlinks between each pair of switches
interlink_redundancy = 2
num_required_slaves = 1


num_links = num_switches * num_slaves
# A clique K_n has n choose 2 = n * (n-1)/2 edges
num_interlinks = interlink_redundancy * num_switches * (num_switches - 1)/2


slaves = tuple(['s' + str(i) for i in range(num_slaves)])
links = tuple(['l' + str(i) for i in range(num_links)])
switches = tuple(['b' + str(i) for i in range(num_switches)])
interlinks = tuple(['i' + str(i) for i in range(num_interlinks)])

def cycle_zip(list1, list2):
    if len(list1) > len(list2):
        return zip(list1, cycle(list2))
    elif len(list1) < len(list2):
        return zip(cycle(list1), list2)
    else:
        return zip(list1, list2)


E = cycle_zip(links, slaves)

for slave in slaves:
    links_of_slave = [a for (a, b) in E if b == slave]
    E.extend(cycle_zip(links_of_slave, switches))

# Create clique of switches interconnected by interlinks
i = 0
for switch1, switch2 in combinations(switches, 2):
    print switch1, switch2
    for j in range(interlink_redundancy):
        E.append((switch1, interlinks[i+j]))
        E.append((switch2, interlinks[i+j]))
    i += interlink_redundancy

G = nx.Graph()
G.add_edges_from(E)

class_to_color = {
    slaves: 'green',
    switches: 'yellow',
    links: 'blue',
    interlinks: 'blue'
}

colorize_graph(G, class_to_color)

save_graph_drawing(G, 'G.png')

mc = generate_mc(G, is_faulty, switches, slaves, num_required_slaves)
save_ctmc_drawing(mc, 'mc.png')

for i in range(5): print
