import glob
import json
import csv
from collections import defaultdict

def compute_transition_probabilities(sequences, include_start=False):
    """
    Given a list of chord sequences (each a list of chord names),
    compute transition probabilities between chords, plus an 'END' state.
    If include_start is True, also count a 'START' → first_chord transition.
    Returns a dict of dicts: { curr_chord: { next_chord_or_'END': probability, … }, … }
    """
    counts   = defaultdict(lambda: defaultdict(int))
    endings  = defaultdict(int)

    # Optionally count transitions from START to the first chord in each sequence
    if include_start:
        for seq in sequences:
            if seq:
                counts['START'][ seq[0] ] += 1

    for seq in sequences:
        for i, chord in enumerate(seq):
            if i + 1 < len(seq):
                counts[chord][ seq[i+1] ] += 1
            else:
                endings[chord] += 1

    probabilities = {}
    for curr, next_counts in counts.items():
        total = sum(next_counts.values()) + endings.get(curr, 0)
        probs = { nxt: cnt/total for nxt, cnt in next_counts.items() }
        if endings.get(curr, 0) > 0:
            probs['END'] = endings[curr] / total
        probabilities[curr] = probs

    return probabilities

if __name__ == "__main__":
    # 1. Load all JSON files
    file_paths   = glob.glob("out_structure3/db_*.json")
    loaded_count = len(file_paths)

    # 2. Extract chord sequences (only those with >4 chords)
    sequences = []
    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as f:
            data   = json.load(f)
            chords = data.get("all-chords-in-c", [])
            if len(chords) > 4:
                sequences.append(chords)
    kept_count = len(sequences)

    # 3. Count total occurrences of each chord
    freq = defaultdict(int)
    for seq in sequences:
        for chord in seq:
            freq[chord] += 1

    # 4. Only keep chords with >500 total occurrences
    valid_chords = { chord for chord, cnt in freq.items() if cnt > 500 }

    # 5. Compute full transition probabilities, including START
    probs = compute_transition_probabilities(sequences, include_start=True)

    # 6. Build ordered list: START, chromatic roots in C, then END
    chromatic_roots = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    # only include those roots that actually appear in valid_chords
    ordered_roots   = [root for root in chromatic_roots if root in valid_chords]

    desired_order = ['START'] + ordered_roots + ['END']

    # 7. Build and print the matrix
    header      = [''] + desired_order
    matrix_rows = []
    for next_chord in desired_order:
        row = [next_chord] + [
            f"{probs.get(curr, {}).get(next_chord, 0.0):.4f}"
            for curr in desired_order
        ]
        matrix_rows.append(row)

    print(f"Loaded {loaded_count} files, kept {kept_count} sequences.")
    print('\t'.join(header))
    for row in matrix_rows:
        print('\t'.join(row))

    # 8. Save to CSV
    with open('chord_transitions.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(matrix_rows)

    print("\nSaved chord transition probabilities to chord_transitions.csv")
