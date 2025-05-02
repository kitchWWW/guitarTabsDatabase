import os
import glob
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Parameters
input_dir      = 'csvTransitionCount'
output_dir     = 'chartTransitionCountFlow'
threshold      = 12000
node_size      = 2800
width_factor   = 0.0001
dpi            = 300  # adjust to 600 for even higher resolution

os.makedirs(output_dir, exist_ok=True)

for csv_path in glob.glob(os.path.join(input_dir, '*.csv')):
    # derive a base name for saving
    base = os.path.splitext(os.path.basename(csv_path))[0]

    # 1) load & filter
    df = pd.read_csv(csv_path, index_col=0)
    df = df[df > df.max().max()/10]
    width_factor = 10 / df.max().max()

    # 2) build directed graph (note: dst → src for flow backward)
    G = nx.DiGraph()
    for src in df.index:
        for dst, w in df.loc[src].items():
            if pd.notna(w):
                G.add_edge(dst, src, weight=w)

    # 3) layout & edge widths
    pos = nx.circular_layout(G)
    all_widths = [G[u][v]['weight'] * width_factor for u, v in G.edges()]

    # 4) prepare label map (e.g. "pre" → "Pre-Chorus")
    label_map = {}
    for node in G.nodes():
        if node.lower() == 'pre':
            label_map[node] = 'Pre-Chorus'
        else:
            label_map[node] = '-'.join(part.capitalize() for part in node.split('-'))

    # start drawing
    plt.figure(figsize=(8, 8))
    nx.draw_networkx_nodes(
        G, pos,
        node_size=node_size,
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

    # classify edges for straight, bidirectional and self-loops
    bidirs = {frozenset((u, v)) for u, v in G.edges() if G.has_edge(v, u)}
    straight, fwd, back, self_loops = [], [], [], []
    straight_w, fwd_w, back_w, self_w = [], [], [], []

    for (u, v), w in zip(G.edges(), all_widths):
        if u == v:
            self_loops.append((u, v));   self_w.append(w)
        elif frozenset((u, v)) in bidirs:
            if u < v:
                fwd.append((u, v));     fwd_w.append(w)
            else:
                back.append((u, v));    back_w.append(w)
        else:
            straight.append((u, v));     straight_w.append(w)

    # 5) draw edges
    arrows_stra = nx.draw_networkx_edges(
        G, pos, edgelist=straight, arrowstyle='-|>', width=straight_w, edge_color='gray', node_size=node_size
    )
    arrows_fwd  = nx.draw_networkx_edges(
        G, pos, edgelist=fwd,     arrowstyle='-|>', connectionstyle='arc3,rad=.2',
        width=fwd_w, edge_color='gray', node_size=node_size
    )
    arrows_back = nx.draw_networkx_edges(
        G, pos, edgelist=back,    arrowstyle='-|>', connectionstyle='arc3,rad=.2',
        width=back_w, edge_color='gray', node_size=node_size
    )
    arrows_self = nx.draw_networkx_edges(
        G, pos, edgelist=self_loops, arrowstyle='-|>', connectionstyle='arc3,rad=0.5',
        width=self_w, edge_color='gray', node_size=node_size
    )

    # 6) tweak arrowheads
    for arrows, widths, extra in [
        (arrows_stra, straight_w, 0),
        (arrows_fwd,  fwd_w,       0),
        (arrows_back, back_w,      0),
        (arrows_self, self_w,     15)
    ]:
        for patch, w in zip(arrows, widths):
            patch.set_mutation_scale(20 + w + extra)
            patch.set_joinstyle('miter')
            patch.set_capstyle('butt')

    plt.axis('off')
    plt.tight_layout()
    # 7) save with high DPI
    out_path = os.path.join(output_dir, f"{base}.png")
    plt.savefig(out_path, dpi=dpi, bbox_inches='tight')
    plt.close()

    print(f"Saved {out_path}")
