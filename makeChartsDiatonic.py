import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# Directories
input_dir  = 'csv'
output_dir = 'charts_diatonic'
os.makedirs(output_dir, exist_ok=True)

for csv_path in glob.glob(os.path.join(input_dir, '*.csv')):
    # 1. Load & transpose
    df = pd.read_csv(csv_path, index_col=0).T

    # — 1.5 Filter out any row/col with “#” in its label —
    df = df.loc[~df.index.str.contains(r"#"),
                ~df.columns.str.contains(r"#")]

    # 2. Create figure & axis
    fig, ax = plt.subplots(figsize=(10, 8))

    # 3. Plot heatmap with fixed color-scale 0→0.4
    heatmap = ax.imshow(df.values,
                        aspect='auto',
                        vmin=0,
                        vmax=0.4)

    # 4. Move x-axis labels to top
    ax.xaxis.tick_top()
    ax.tick_params(axis='x', which='both', bottom=False, top=True)

    # 5. Set tick labels
    ax.set_xticks(range(len(df.columns)))
    ax.set_yticks(range(len(df.index)))
    ax.set_xticklabels(df.columns, rotation=45, ha='left')
    ax.set_yticklabels(df.index)

    # 6. Annotate each cell with real values
    threshold = df.values.max() / 2
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            pct = df.iat[i, j] * 100
            ax.text(
                j, i, f"{pct:.2f}%",
                ha='center', va='center', fontsize=8,
                color='white' if df.iat[i, j] < threshold else 'black'
            )

    # 7. Colorbar (extend indicates >0.4 values)
    cbar = fig.colorbar(heatmap, ax=ax, extend='max')
    cbar.set_label('Probability')

    # 8. Layout & save
    plt.tight_layout()
    basename = os.path.splitext(os.path.basename(csv_path))[0]
    out_path = os.path.join(output_dir, f"{basename}.png")
    fig.savefig(out_path, dpi=300)
    plt.close(fig)

    print(f"Saved {out_path}")
