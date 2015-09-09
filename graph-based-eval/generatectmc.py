import networkx as nx
import matplotlib.pyplot as plt


def save_graph_drawing(graph, filename, labels=None, graph_layout='spring',
               node_size=1600, node_color='blue', node_alpha=0.3,
               node_text_size=12,
               edge_color='blue', edge_alpha=0.3, edge_tickness=1,
               edge_text_pos=0.3,
               text_font='sans-serif'):

    if graph_layout == 'shell':
        graph_pos=nx.shell_layout(graph)
    elif graph_layout == 'spectral':
        graph_pos=nx.spectral_layout(graph)
    elif graph_layout == 'random':
        graph_pos=nx.random_layout(graph)
    else:
        graph_pos=nx.spring_layout(graph)

    # draw graph
    nx.draw_networkx_nodes(graph,graph_pos,node_size=node_size,
                           alpha=node_alpha, node_color=node_color)
    nx.draw_networkx_edges(graph,graph_pos,width=edge_tickness,
                           alpha=edge_alpha,edge_color=edge_color)
    nx.draw_networkx_labels(graph, graph_pos,font_size=node_text_size,
                            font_family=text_font)

    # show graph
    plt.savefig(filename)

def is_faulty(G, num_necessary_slaves):
    """
    num_necessary_slaves: minimum number of slaves that must be connected to
    each other in graph G for G not to be faulty.
    """
    num_slaves_cc1 = num_slaves_cc2 = 0
    if 'b1' in G.nodes():
        cc1 = nx.node_connected_component(G, 'b1')
        for v in cc1:
            if v in slaves:
                num_slaves_cc1 = num_slaves_cc1 + 1
    if 'b2' in G.nodes():
        cc2 = nx.node_connected_component(G, 'b2')
        for v in cc2:
            if v in slaves:
                num_slaves_cc2 = num_slaves_cc2 + 1
    return not (
        num_slaves_cc1 >= num_necessary_slaves or
        num_slaves_cc2 >= num_necessary_slaves)


def extract_node(G, v):
    for n in G.neighbors(v):
        G.remove_node(n)
    G.remove_node(v)


slaves = ['s1', 's2']
switches = ['b1', 'b2']

E = [('s1', 'l1'), ('s1', 'l2'), ('l1', 'b1'), ('l2', 'b2'),
     ('b1', 'l5'), ('l5', 'b2'), ('b1', 'l6'), ('l6', 'b2'),
     ('s2', 'l3'), ('s2', 'l4'), ('l3', 'b1'), ('l4', 'b2')]
G = nx.Graph()
G.add_edges_from(E)

save_graph_drawing(G, 'G.png')

print is_faulty(G, 2)
