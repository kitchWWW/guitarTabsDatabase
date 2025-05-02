import os
import pandas as pd
import matplotlib.pyplot as plt

# 1) Load the CSV, using the first column ("Section") as the index
df = pd.read_csv('csvCounts/chord_counts_percent_by_section.csv', index_col=0)

# 2) Make sure the output directory exists
out_dir = 'chartsCounts'
os.makedirs(out_dir, exist_ok=True)

# 3) For each section (row), plot and save a bar chart
for section, freqs in df.iterrows():
    # Prepare figure: size in inches, high pixel density via dpi
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Plot bar chart
    ax.bar(freqs.index, freqs.values, edgecolor='black')
    
    # Labels and title
    ax.set_xlabel('Pitch Class')
    ax.set_ylabel('Frequency')
    ax.set_title(f'{section.capitalize()} — Chord Frequencies')
    
    # Make sure labels don’t overlap
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save and close
    out_path = os.path.join(out_dir, f'{section}.png')
    fig.savefig(out_path)
    plt.close(fig)

print(f'Bar charts written to {out_dir}/') 
