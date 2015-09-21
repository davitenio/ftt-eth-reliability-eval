import networkx as nx
from generatectmc import *


slaves = ('s1', 's2')
switches = ('b1', 'b2')
links = ('l1', 'l2', 'l3', 'l4', 'l5', 'l6')

E = [('s1', 'l1'), ('s1', 'l2'), ('l1', 'b1'), ('l2', 'b2'),
     ('b1', 'l5'), ('l5', 'b2'), ('b1', 'l6'), ('l6', 'b2'),
     ('s2', 'l3'), ('s2', 'l4'), ('l3', 'b1'), ('l4', 'b2')]
G = nx.Graph()
G.add_edges_from(E)

class_to_color = {
    slaves: 'green',
    switches: 'yellow',
    links: 'blue'
}

colorize_graph(G, class_to_color)

save_graph_drawing(G, 'G.png')

mc = generate_mc(G, is_faulty, switches, slaves, 1)
save_ctmc_drawing(mc, 'mc.png')

for i in range(5): print
