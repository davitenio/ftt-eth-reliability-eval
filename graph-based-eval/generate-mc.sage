def is_faulty(G, k):
    slaves_cc1 = slaves_cc2 = []
    if 'b1' in G.vertices():
        cc1 = G.connected_component_containing_vertex('b1')
        slaves_cc1 = [v for v in cc1 if v in slaves]
    if 'b2' in G.vertices():
        cc2 = G.connected_component_containing_vertex('b2')
        slaves_cc2 = [v for v in cc2 if v in slaves]
    return not (len(slaves_cc1) >= k or len(slaves_cc2) >= k)

def explore(G, mc, is_faulty, *args):
    for v in G.vertices():
        H = G.copy()
        H.delete_vertex(v)
        print "Deleted vertex {}".format(v)
        H.name(str(H.vertices()))
        Gi = G.copy(immutable=True)
        Hi = H.copy(immutable=True)
        Fi = Graph(immutable=True)
        if Hi in mc.vertices():
            print "Graph {} is already in MC".format(Hi)
            continue
        if is_faulty(H, *args):
            mc.add_edge(Gi, Fi, label=str(v))
        else:
            mc.add_vertex(Hi)
            mc.add_edge(Gi, Hi, label=str(v))
            explore(H, mc, is_faulty, *args)

def generate_mc(G, is_faulty, *args):
    if is_faulty(G, *args):
        return None
    mc = DiGraph()
    # initial graph
    Gi = G.copy(immutable=True)
    # empty graph (corresponding to the failure state)
    Fi = Graph(immutable=True, name="F")
    mc.add_vertex(Gi)
    mc.add_vertex(Fi)
    explore(G, mc, is_faulty, *args)
    return mc


slaves = ['s1', 's2']
switches = ['b1', 'b2']

E = [('s1', 'l1'), ('s1', 'l2'), ('l1', 'b1'), ('l2', 'b2'),
     ('b1', 'l5'), ('l5', 'b2'), ('b1', 'l6'), ('l6', 'b2'),
     ('s2', 'l3'), ('s2', 'l4'), ('l3', 'b1'), ('l4', 'b2')]
G = Graph(E)


for v in ['s2', 'l3', 'l4', 'l6', 'l2']:
    G.delete_vertex(v)
G.name(str(G.vertices()))
G.plot().save('G.png')

mc = generate_mc(G, is_faulty, 1)
if mc is None: print "Empty MC"
else: mc.plot(edge_labels=True, edge_color="gray").save('mc.png')

state_space = mc.vertices()
print state_space
graphs_list.to_graphics_array(state_space).save('graphs.png')
