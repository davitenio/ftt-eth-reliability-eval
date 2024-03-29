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
               edge_alpha=0.3, edge_tickness=1,
               edge_text_pos=0.3,
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

    colors = []
    for vertex in graph.nodes():
        try:
            colors.append(graph.node[vertex]['color'])
        except KeyError:
            colors.append('white')

    nx.draw_networkx_nodes(graph, graph_pos, node_size=node_size,
                           alpha=node_alpha, node_color=colors, ax=axis)

    nx.draw_networkx_edges(graph, graph_pos, width=edge_tickness,
                           alpha=edge_alpha, edge_color='blue',
                           arrows=True, ax=axis)
    nx.draw_networkx_labels(graph, graph_pos, font_size=node_text_size,
                            font_family=text_font, ax=axis)

    plt.axis('off')

    plt.savefig(filename)


def is_faulty(G, indicator, indicator_args):
    """
    G is correct (non-faulty) if it has exactly 1 non-faulty connected
    component. Having more than 1 correct component is considered a failure
    because we assume that if the system is split into more than one
    functioning subsystem, this is a failure.
    """
    num_non_faulty_cc = 0
    for component in nx.connected_component_subgraphs(G, copy=False):
        if indicator(component, *indicator_args):
            num_non_faulty_cc += 1
    if num_non_faulty_cc == 1:
        return False
    else:
        return True


def add_rate(ctmc, src_state, dst_state, failed_element):
    if ctmc.has_edge(src_state, dst_state):
        ctmc.edge[src_state][dst_state]['failed_element'].append(failed_element)
    else:
        ctmc.add_edge(src_state, dst_state, failed_element=[failed_element])


def colors_match(n1_attribute, n2_attribute):
    return n1_attribute['color'] == n2_attribute['color']


def get_color_isomorphic_state(ctmc, H):
    """
    Return a state of the continuous-time Markov chain ctmc that is a graph
    which is isomorphic to the graph H.
    """
    for state in ctmc.nodes_iter():
        if nx.is_isomorphic(H, state, node_match=colors_match):
            return state
    return None


def delete_vertex_set(G, vertex_set):
    """
    Delete the vertices in vertex_set from G.
    """
    for vertex in vertex_set:
        G.remove_node(vertex)


def strip_faulty_components(G, indicator, indicator_args):
    """
    Delete all connected components of G that are faulty according to the
    function indicator when called with indicator_args.
    """
    cc_subgraphs = nx.connected_component_subgraphs(G, copy=False)
    for cc in list(cc_subgraphs):
        if not indicator(cc, *indicator_args):
            delete_vertex_set(G, cc.nodes_iter())


def explore(ctmc, G, failure_state, indicator, indicator_args):
    """
    ctmc: continuous-time Markov Chain that is being built.
    G:
    failure_state: empty graph corresponding to an absorbing failure state.
    indicator: callback function that distinguishes faulty from non-faulty
        graphs.
    indicator_args: arguments for the callback function indicator.
    """
    for vertex in G.nodes_iter():
        # Use nx.Graph(G) to do a shallow copy. G.copy() would do a deep copy.
        H = nx.Graph(G)
        H.remove_node(vertex)

        strip_faulty_components(H, indicator, indicator_args)

        if nx.number_connected_components(H) != 1:
            add_rate(ctmc, G, failure_state, vertex)
            continue

        color_isomorphic_state = get_color_isomorphic_state(ctmc, H)

        current_state = G
        if color_isomorphic_state == None:
            # Create new state in ctmc and add a transition to it
            new_state = H
            ctmc.add_node(new_state)
            add_rate(ctmc, current_state, new_state, vertex)
            explore(ctmc, new_state, failure_state, indicator, indicator_args)
        else:
            # Update existing transition in ctmc
            add_rate(ctmc, current_state, color_isomorphic_state, vertex)


def generate_ctmc(G, indicator, indicator_args):
    if is_faulty(G, indicator, indicator_args):
        return None
    ctmc = nx.DiGraph()
    # empty graph (corresponding to the failure state)
    F = nx.Graph()
    ctmc.add_nodes_from([G, F])
    explore(ctmc, G, F, indicator, indicator_args)
    return ctmc


def colorize_graph(G, class_to_color):
    for vertex in G.nodes_iter():
        for equivalence_class, class_color in class_to_color.items():
            if vertex in equivalence_class:
                G.node[vertex]['color'] = class_color
