import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

# 1) load & filter
df = pd.read_csv('chord_transitions.csv', index_col=0)
df = df[df > 0.16]

# 2) build directed graph
G = nx.DiGraph()
for src in df.index:
    for dst, p in df.loc[src].items():
        if not pd.isna(p):
            G.add_edge(dst, src, weight=p)

# 3) layout & edge widths
pos = nx.circular_layout(G)
node_sz = 2800
width_factor = 10
# full list of widths in same order as G.edges()
all_widths = [G[u][v]['weight'] * width_factor for u, v in G.edges()]

# 4) prepare label map (pre → Pre-Chorus, title-case)
label_map = {}
for node in G.nodes():
    if node.lower() == 'pre':
        label_map[node] = 'Pre-Chorus'
    else:
        label_map[node] = '-'.join(part.capitalize() for part in node.split('-'))

plt.figure(figsize=(8,8))

# 5) draw nodes & labels
nx.draw_networkx_nodes(
    G, pos,
    node_size=node_sz,
    node_color='white',
    edgecolors='black',
    linewidths=1
)
nx.draw_networkx_labels(
    G, pos,
    labels=label_map,
    font_size=12,
    font_color='black',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='none')
)

# 6) classify edges
bidirs = {frozenset((u, v)) for u, v in G.edges() if G.has_edge(v, u)}
self_edges, self_widths = [], []
straight_edges, fwd_edges, back_edges = [], [], []
straight_widths, fwd_widths, back_widths = [], [], []

for (u, v), w in zip(G.edges(), all_widths):
    if u == v:
        # this is a self‐loop!
        self_edges.append((u, v))
        self_widths.append(w)
    elif frozenset((u, v)) in bidirs:
        if u < v:
            fwd_edges.append((u, v));  fwd_widths.append(w)
        else:
            back_edges.append((u, v)); back_widths.append(w)
    else:
        straight_edges.append((u, v)); straight_widths.append(w)


# 7) draw straight edges
arrows_straight = nx.draw_networkx_edges(
    G, pos,
    edgelist=straight_edges,
    arrowstyle='-|>',
    width=straight_widths,
    edge_color='gray',
    node_size=node_sz
)

# 8) draw curved edges (rad positive for fwd, negative for back)
arrows_fwd = nx.draw_networkx_edges(
    G, pos,
    edgelist=fwd_edges,
    arrowstyle='-|>',
    connectionstyle='arc3,rad=.2',
    width=fwd_widths,
    edge_color='gray',
    node_size=node_sz
)
arrows_back = nx.draw_networkx_edges(
    G, pos,
    edgelist=back_edges,
    arrowstyle='-|>',
    connectionstyle='arc3,rad=.2',
    width=back_widths,
    edge_color='gray',
    node_size=node_sz
)
arrows_self = nx.draw_networkx_edges(
    G, pos,
    edgelist=self_edges,
    arrowstyle='-|>',
    connectionstyle='arc3,rad=0.5',  # bigger loop
    width=self_widths,
    edge_color='gray',
    node_size=node_sz
)


# 9) tweak all arrow patches for crispness
for arrows, widths, extra in [
    (arrows_straight, straight_widths,   0),
    (arrows_fwd,      fwd_widths,        0),
    (arrows_back,     back_widths,       0),
    (arrows_self,     self_widths,       15)  # +15 for noticeably larger heads
]:
    for patch, w in zip(arrows, widths):
        patch.set_mutation_scale(20 + w + extra)
        patch.set_joinstyle('miter')
        patch.set_capstyle('butt')

plt.axis('off')
plt.tight_layout()
plt.show()