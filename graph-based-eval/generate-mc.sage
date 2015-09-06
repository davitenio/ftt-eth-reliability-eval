def is_faulty(G, k):
    slaves_cc1 = slaves_cc2 = []
    if 'b1' in G.vertex_iterator():
        cc1 = G.connected_component_containing_vertex('b1')
        slaves_cc1 = [v for v in cc1 if v in slaves]
    if 'b2' in G.vertex_iterator():
        cc2 = G.connected_component_containing_vertex('b2')
        slaves_cc2 = [v for v in cc2 if v in slaves]
    return not (len(slaves_cc1) >= k or len(slaves_cc2) >= k)

def extract_vertex(G, v):
    for n in G.neighbor_iterator(v):
        G.delete_vertex(n)
    G.delete_vertex(v)

def explore(G, mc, extractable_vertices, is_faulty, *args):
    for v in G.vertex_iterator():
        H = G.copy()
        if v in extractable_vertices:
            extract_vertex(H, v)
            print "Extracted vertex {}".format(v)
        else:
            H.delete_vertex(v)
            print "Deleted vertex {}".format(v)
        H.name("-".join(H.vertex_iterator()))
        Gi = G.copy(immutable=True)
        Hi = H.copy(immutable=True)
        Fi = Graph(immutable=True)
        if Hi in mc.vertex_iterator():
            print "Graph {} is already in MC".format(Hi)
            assert not mc.has_edge(Gi, Hi)
            mc.add_edge(Gi, Hi, label=str(v))
        elif is_faulty(H, *args):
            new_label = str(v)
            if mc.has_edge(Gi, Fi):
                print "MC already has edge {}".format((Gi, Hi))
                old_label = mc.edge_label(Gi, Fi)
                new_label = "{}, {}".format(old_label, new_label)
            mc.add_edge(Gi, Fi, label=new_label)
        else:
            mc.add_vertex(Hi)
            mc.add_edge(Gi, Hi, label=str(v))
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
