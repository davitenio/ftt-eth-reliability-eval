import networkx as nx
import matplotlib.pyplot as plt


def save_ctmc_drawing(ctmc_graph, filename, labels=None, graph_layout='shell',
               node_size=1600, node_color='gray', node_alpha=0.3,
               node_text_size=8,
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
        edge_labels[e] = ctmc_graph.edge[e[0]][e[1]]['failed_element']
    nx.draw_networkx_edge_labels(ctmc_graph, graph_pos, edge_labels,
                            font_size=node_text_size, font_family=text_font,
                            ax=axis)


    plt.axis('off')

    plt.savefig(filename, bbox_inches="tight")


def save_graph_drawing(graph, filename, labels=None, graph_layout='spring',
               node_size=1600, node_alpha=0.3,
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

    colors = [graph.node[vertex]['color'] for vertex in graph.nodes()]

    nx.draw_networkx_nodes(graph, graph_pos, node_size=node_size,
                           alpha=node_alpha, node_color=colors, ax=axis)
    nx.draw_networkx_edges(graph, graph_pos, width=edge_tickness,
                           alpha=edge_alpha, edge_color=edge_color,
                           arrows=arrows, ax=axis)
    nx.draw_networkx_labels(graph, graph_pos, font_size=node_text_size,
                            font_family=text_font, ax=axis)

    plt.axis('off')

    plt.savefig(filename)

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


def add_rate(mc, src_state, dst_state, failed_element):
    if mc.has_edge(src_state, dst_state):
        print "MC already has edge {}".format(
            (sorted(src_state.nodes()), sorted(dst_state.nodes())))
        mc.edge[src_state][dst_state]['failed_element'].append(failed_element)
    else:
        mc.add_edge(src_state, dst_state, failed_element=[failed_element])
    print "Rate is {}".format(mc.edge[src_state][dst_state]['failed_element'])


def colors_match(n1_attrib, n2_attrib):
    return n1_attrib['color']==n2_attrib['color']


def explore(G, F, mc, is_faulty, *args):
    print "New recursion"
    print sorted(G.nodes())
    for v in G.nodes_iter():
        print "Vertex: {}".format(v)
        H = G.copy()
        H.remove_node(v)
        print "Deleted vertex {}".format(v)

        cc_subgraphs = nx.connected_component_subgraphs(H)
        for cc in cc_subgraphs:
            if is_faulty(cc, *args):
                for cc_vertex in cc.nodes_iter():
                    H.remove_node(cc_vertex)

        if is_faulty(H, *args):
            print "Adding transition from {} to faulty state".format(
                sorted(G.nodes()))
            add_rate(mc, G, F, v)
            continue

        for state in mc.nodes_iter():
            if nx.is_isomorphic(state, H, node_match=colors_match):
                print "MC already has state isomorphic to {}".format(
                    sorted(H.nodes()))
                print "Adding transition from {} to {}".format(
                    sorted(G.nodes()), sorted(state.nodes()))
                add_rate(mc, G, state, v)
                break
        else:
            print "Adding new state {}".format(sorted(H.nodes()))
            mc.add_node(H)
            print "Adding transition from {} to {}".format(
                sorted(G.nodes()), sorted(H.nodes()))
            add_rate(mc, G, H, v)
            explore(H, F, mc, is_faulty, *args)
            print "Backtracking"
            print sorted(G.nodes())


def generate_mc(G, is_faulty, *args):
    if is_faulty(G, *args):
        return None
    mc = nx.DiGraph()
    # empty graph (corresponding to the failure state)
    F = nx.Graph()
    mc.add_nodes_from([G, F])
    explore(G, F, mc, is_faulty, *args)
    return mc


def colorize_graph(G, class_to_color):
    for vertex in G.nodes_iter():
        for equivalence_class, class_color in class_to_color.items():
            if vertex in equivalence_class:
                G.node[vertex]['color'] = class_color
