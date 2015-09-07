def is_faulty(G, num_necessary_slaves):
    """
    num_necessary_slaves: minimum number of slaves that must be connected to
    each other in graph G for G not to be faulty.
    """
    num_slaves_cc1 = num_slaves_cc2 = 0
    if 'b1' in G.vertex_iterator():
        cc1 = G.connected_component_containing_vertex('b1')
        for v in cc1:
            if v in slaves:
                num_slaves_cc1 = num_slaves_cc1 + 1
    if 'b2' in G.vertex_iterator():
        cc2 = G.connected_component_containing_vertex('b2')
        for v in cc2:
            if v in slaves:
                num_slaves_cc2 = num_slaves_cc2 + 1
    return not (
        num_slaves_cc1 >= num_necessary_slaves or
        num_slaves_cc2 >= num_necessary_slaves)


def extract_vertex(G, v):
    for n in G.neighbor_iterator(v):
        G.delete_vertex(n)
    G.delete_vertex(v)


def add_rate(mc, src_state, dst_state, rate):
    new_label = rate
    if mc.has_edge(src_state, dst_state):
        print "MC already has edge {}".format((src_state, dst_state))
        old_label = mc.edge_label(src_state, dst_state)
        new_label = "{}, {}".format(old_label, new_label)
    mc.add_edge(src_state, dst_state, label=new_label)


def explore(G, mc, extractable_vertices, is_faulty, *args):
    for v in G.vertex_iterator():
        H = G.copy()
        if v in extractable_vertices:
            extract_vertex(H, v)
            print "Extracted vertex {}".format(v)
        else:
            H.delete_vertex(v)
            print "Deleted vertex {}".format(v)
        cc_subgraphs = H.connected_components_subgraphs()
        for cc in cc_subgraphs:
            if is_faulty(cc, *args):
                for cc_vertex in cc:
                    H.delete_vertex(cc_vertex)
        H.name("-".join(H.vertex_iterator()))
        Gi = G.copy(immutable=True)
        Hi = H.copy(immutable=True)
        Fi = Graph(immutable=True)

        if is_faulty(H, *args):
            add_rate(mc, Gi, Fi, str(v))
        elif Hi in mc.vertex_iterator():
            add_rate(mc, Gi, Hi, str(v))
        else:
            mc.add_vertex(Hi)
            add_rate(mc, Gi, Hi, str(v))
            explore(H, mc, extractable_vertices, is_faulty, *args)


def generate_mc(G, extractable_vertices, is_faulty, *args):
    if is_faulty(G, *args):
        return None
    mc = DiGraph()
    # initial graph
    Gi = G.copy(immutable=True)
    # empty graph (corresponding to the failure state)
    Fi = Graph(immutable=True, name="F")
    mc.add_vertex(Gi)
    mc.add_vertex(Fi)
    explore(G, mc, extractable_vertices, is_faulty, *args)
    return mc


slaves = ['s1', 's2']
switches = ['b1', 'b2']

E = [('s1', 'l1'), ('s1', 'l2'), ('l1', 'b1'), ('l2', 'b2'),
     ('b1', 'l5'), ('l5', 'b2'), ('b1', 'l6'), ('l6', 'b2'),
     ('s2', 'l3'), ('s2', 'l4'), ('l3', 'b1'), ('l4', 'b2')]
G = Graph(E)


for v in ['b2', 'l5', 'l4', 'l6', 'l2']:
    G.delete_vertex(v)
G.name("-".join(G.vertices()))
G.plot().save('G.png')

mc = generate_mc(G, slaves + switches, is_faulty, 1)
if mc is None: print "Empty MC"
else: mc.plot(edge_labels=True, edge_color="gray").save('mc.png')

state_space = mc.vertices()
for H in state_space:
    plot = H.plot()
    filename = H.name() + ".png"
    plot.save(filename)
graphs_list.to_graphics_array(state_space).save('graphs.png')
print mc.order()
