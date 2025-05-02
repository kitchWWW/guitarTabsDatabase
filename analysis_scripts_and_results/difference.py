import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

# Directories
input_dir        = 'csv'
full_csv_path    = os.path.join(input_dir, 'chord_transitions_full.csv')
output_csv_dir   = 'differencecsv'
output_chart_dir = 'differencechart'

os.makedirs(output_csv_dir, exist_ok=True)
os.makedirs(output_chart_dir, exist_ok=True)

# Parameter: clip heatmap at ± this fraction
range_of_thing = 0.2  # 20%

# Load the “full” reference matrix once
full_df = pd.read_csv(full_csv_path, index_col=0)

# Process each CSV in input_dir
for csv_path in glob.glob(os.path.join(input_dir, '*.csv')):
    basename = os.path.basename(csv_path)
    if basename == os.path.basename(full_csv_path):
        continue  # skip the full reference file

    name = os.path.splitext(basename)[0]
    # derive a pretty display name
    display_name = name.replace('_', ' ')

    # 1. Read current matrix
    curr_df = pd.read_csv(csv_path, index_col=0)

    # 2. Compute difference (current minus full) and transpose
    diff = (curr_df - full_df).T

    # 3. Filter out any row/col with “#” or named "END"
    mask_rows = ~diff.index.str.contains(r"#")
    mask_cols = ~diff.columns.str.contains(r"#")
    diff = diff.loc[mask_rows, mask_cols]

    # 4. Save diff to CSV
    out_csv = os.path.join(output_csv_dir, f'{name}_difference.csv')
    diff.to_csv(out_csv)

    # 5. Plot heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    heatmap = ax.imshow(
        diff.values,
        aspect='auto',
        cmap='RdYlGn',
        vmin=-range_of_thing,
        vmax= range_of_thing
    )

    # Add the filename (pretty) as the title
    ax.set_title(display_name, pad=20)

    # Move x‐axis labels to top
    ax.xaxis.tick_top()
    ax.tick_params(axis='x', which='both', bottom=False, top=True)

    # Label ticks
    ax.set_xticks(range(len(diff.columns)))
    ax.set_xticklabels(diff.columns, rotation=45, ha='left')
    ax.set_yticks(range(len(diff.index)))
    ax.set_yticklabels(diff.index)

    # Annotate each cell with percent difference
    annot_thresh = 0.1  # switch text color above 10%
    for i in range(diff.shape[0]):
        for j in range(diff.shape[1]):
            val = diff.iat[i, j]
            txt = f"{val * 100:.1f}%"
            color = 'white' if abs(val) > annot_thresh else 'black'
            ax.text(j, i, txt, ha='center', va='center', fontsize=8, color=color)

    # Colorbar
    cbar = fig.colorbar(heatmap, ax=ax)
    cbar.set_label(f'Difference (clipped ±{range_of_thing*100:.0f}%)')

    # Save figure
    out_png = os.path.join(output_chart_dir, f'{name}_difference.png')
    fig.tight_layout(rect=[0, 0, 1, 0.95])  # leave room for title
    fig.savefig(out_png, dpi=300)
    plt.close(fig)

    print(f"→ Saved {out_csv} and {out_png}")
