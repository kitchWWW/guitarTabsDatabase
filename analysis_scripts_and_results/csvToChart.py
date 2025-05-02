import pandas as pd
import matplotlib.pyplot as plt

# 1. Load & transpose the matrix to swap rows ↔ columns
df = pd.read_csv('chord_transitions.csv', index_col=0).T

# 2. Create figure & axis
fig, ax = plt.subplots(figsize=(10, 8))

# 3. Plot as a heatmap
heatmap = ax.imshow(df.values, aspect='auto')

# 4. Move the x-axis tick labels to the top
ax.xaxis.tick_top()
ax.tick_params(axis='x', which='both', bottom=False, top=True)

# 5. Set tick labels on both axes
ax.set_xticks(range(len(df.columns)))
ax.set_yticks(range(len(df.index)))
ax.set_xticklabels(df.columns, rotation=45, ha='left')  # labels now on top
ax.set_yticklabels(df.index)

# 6. Annotate each cell, **inverting** the contrast test (`<` instead of `>`)
threshold = df.values.max() / 2
for i in range(df.shape[0]):
    for j in range(df.shape[1]):
        pct = df.iat[i, j] * 100
        ax.text(
            j, i, f"{pct:.2f}%",
            ha='center', va='center', fontsize=8,
            # inverted: white text on cells below threshold, black on cells above
            color='white' if df.iat[i, j] < threshold else 'black'
        )

# 7. Add colorbar & layout tweak
fig.colorbar(heatmap, ax=ax)
plt.tight_layout()
plt.show()
