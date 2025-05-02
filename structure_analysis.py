import glob
import json
import csv
from collections import defaultdict

def compute_transition_probabilities(sequences, include_start=False):
    """
    Given a list of sequences (each a list of strings like "chorus-1"),
    compute transition probabilities between part types (ignoring numeric suffixes).
    If include_start is True, also count a "start" → first_part transition.
    Returns a dict of dicts:
      { current_part_type: { next_part_type_or_'END': probability, … }, … }
    """
    counts = defaultdict(lambda: defaultdict(int))
    endings = defaultdict(int)

    # Count transitions from "start" to the first part
    if include_start:
        for seq in sequences:
            if seq:
                first = seq[0].split('-', 1)[0]
                counts['start'][first] += 1

    # Count all internal transitions and endings
    for seq in sequences:
        for i, part in enumerate(seq):
            curr = part.split('-', 1)[0]
            if i + 1 < len(seq):
                nxt = seq[i + 1].split('-', 1)[0]
                counts[curr][nxt] += 1
            else:
                endings[curr] += 1

    # Build probability table
    probabilities = {}
    for curr, next_counts in counts.items():
        total = sum(next_counts.values()) + endings.get(curr, 0)
        probs = {}
        for nxt, cnt in next_counts.items():
            probs[nxt] = cnt / total
        if endings.get(curr, 0) > 0:
            probs['END'] = endings[curr] / total
        probabilities[curr] = probs

    return probabilities

if __name__ == "__main__":
    # 1. Load all files matching the pattern
    file_paths = glob.glob("out_structure/db_*.json")
    loaded_count = len(file_paths)

    # 2. Extract the 'order' list from each JSON and filter sequences of length ≥ 3
    sequences = []
    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            order = data.get("order", [])
            if len(order) >= 3:
                sequences.append(order)
    kept_count = len(sequences)

    # 3. Compute transition probabilities, including 'start'
    probs = compute_transition_probabilities(sequences, include_start=True)

    # 4. Specify the order of parts for both rows and columns.
    #    Edit this list to control the CSV layout.
    desired_order = [
        'start',
        'intro',
        'verse',
        'chorus',
        'bridge',
        'pre',
        'solo',
        'END'
    ]

    # 5. Build a 2D matrix using that order, rounding to 4 decimals
    header = [''] + desired_order
    matrix_rows = []
    for part in desired_order:
        row = [part]
        for ant in desired_order:
            # Note: if ant not in probs, get returns {} so .get returns 0.0
            p = probs.get(ant, {}).get(part, 0.0)
            row.append(f"{p:.4f}")
        matrix_rows.append(row)

    # 6. Print matrix to console
    print(f"Loaded {loaded_count} files, kept {kept_count} sequences.\n")
    print('\t'.join(header))
    for row in matrix_rows:
        print('\t'.join(row))

    # 7. Save matrix as CSV
    with open('transition_matrix.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(matrix_rows)

    print("\nSaved transition probabilities to transition_matrix.csv")
