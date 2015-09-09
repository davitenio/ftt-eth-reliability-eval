import networkx as nx
import matplotlib.pyplot as plt


def save_ctmc_drawing(ctmc_graph, filename, labels=None, graph_layout='shell',
               node_size=1600, node_color='gray', node_alpha=0.3,
               node_text_size=10,
               edge_color='gray', edge_alpha=0.3, edge_tickness=1,
               edge_text_pos=0.3,
               text_font='sans-serif'):

    figure, axis = plt.subplots()

    if graph_layout == 'shell':
        graph_pos=nx.shell_layout(ctmc_graph)
    elif graph_layout == 'spectral':
        graph_pos=nx.spectral_layout(ctmc_graph)
    elif graph_layout == 'random':
        graph_pos=nx.random_layout(ctmc_graph)
    else:
        graph_pos=nx.spring_layout(ctmc_graph)

    nx.draw_networkx_nodes(ctmc_graph, graph_pos, node_size=node_size,
                           alpha=node_alpha, node_color=node_color, ax=axis)
    nx.draw_networkx_edges(ctmc_graph, graph_pos, width=edge_tickness,
                           alpha=edge_alpha, edge_color=edge_color,
                           arrows=True, ax=axis)

    state_labels = {}
    for state_graph in ctmc_graph.nodes_iter():
        state_labels[state_graph] = sorted(state_graph.nodes_iter())
    nx.draw_networkx_labels(ctmc_graph, graph_pos, state_labels,
                            font_size=node_text_size, font_family=text_font,
                            ax=axis)

    edge_labels = {}
    for e in ctmc_graph.edges_iter():
        edge_labels[e] = mc.edge[e[0]][e[1]]['failed_element']
    nx.draw_networkx_edge_labels(ctmc_graph, graph_pos, edge_labels,
                            font_size=node_text_size, font_family=text_font,
                            ax=axis)


    plt.axis('off')

    plt.savefig(filename)


def save_graph_drawing(graph, filename, labels=None, graph_layout='spring',
               node_size=1600, node_color='blue', node_alpha=0.3,
               node_text_size=12,
               edge_color='blue', edge_alpha=0.3, edge_tickness=1,
               edge_text_pos=0.3, arrows=False,
               text_font='sans-serif'):

    figure, axis = plt.subplots()

    if graph_layout == 'shell':
        graph_pos=nx.shell_layout(graph)
    elif graph_layout == 'spectral':
        graph_pos=nx.spectral_layout(graph)
    elif graph_layout == 'random':
        graph_pos=nx.random_layout(graph)
    else:
        graph_pos=nx.spring_layout(graph)

    nx.draw_networkx_nodes(graph, graph_pos, node_size=node_size,
                           alpha=node_alpha, node_color=node_color, ax=axis)
    nx.draw_networkx_edges(graph, graph_pos, width=edge_tickness,
                           alpha=edge_alpha, edge_color=edge_color,
                           arrows=arrows, ax=axis)
    nx.draw_networkx_labels(graph, graph_pos, font_size=node_text_size,
                            font_family=text_font, ax=axis)

    plt.axis('off')

    plt.savefig(filename)

def is_faulty(G, num_necessary_slaves):
    """
    num_necessary_slaves: minimum number of slaves that must be connected to
    each other in graph G for G not to be faulty.
    """
    num_slaves_cc1 = num_slaves_cc2 = 0
    if 'b1' in G.nodes_iter():
        cc1 = nx.node_connected_component(G, 'b1')
        for v in cc1:
            if v in slaves:
                num_slaves_cc1 = num_slaves_cc1 + 1
    if 'b2' in G.nodes_iter():
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


def add_rate(mc, src_state, dst_state, failed_element):
    if mc.has_edge(src_state, dst_state):
        print "MC already has edge {}".format((src_state, dst_state))
        mc.edge[src_state][dst_state]['failed_element'].append(failed_element)
    mc.add_edge(src_state, dst_state, failed_element=[failed_element])


def explore(G, F, mc, extractable_vertices, is_faulty, *args):
    for v in G.nodes_iter():
        H = G.copy()
        if v in extractable_vertices:
            extract_node(H, v)
            print "Extracted vertex {}".format(v)
        else:
            H.remove_node(v)
            print "Deleted vertex {}".format(v)

        if is_faulty(H, *args):
            add_rate(mc, G, F, v)
        elif H in mc.nodes_iter():
            add_rate(mc, G, H, v)
        else:
            mc.add_node(H)
            add_rate(mc, G, H, v)
            explore(H, F, mc, extractable_vertices, is_faulty, *args)


def generate_mc(G, extractable_vertices, is_faulty, *args):
    if is_faulty(G, *args):
        return None
    mc = nx.DiGraph()
    # empty graph (corresponding to the failure state)
    F = nx.Graph()
    mc.add_nodes_from([G, F])
    explore(G, F, mc, extractable_vertices, is_faulty, *args)
    return mc


slaves = ['s1', 's2']
switches = ['b1', 'b2']

E = [('s1', 'l1'), ('s1', 'l2'), ('l1', 'b1'), ('l2', 'b2'),
     ('b1', 'l5'), ('l5', 'b2'), ('b1', 'l6'), ('l6', 'b2'),
     ('s2', 'l3'), ('s2', 'l4'), ('l3', 'b1'), ('l4', 'b2')]
G = nx.Graph()
G.add_edges_from(E)

G.remove_nodes_from(['b2', 'l5', 'l6', 'l2', 'l4'])

save_graph_drawing(G, 'G.png')

mc = generate_mc(G, [], is_faulty, 1)
save_ctmc_drawing(mc, 'mc.png')
