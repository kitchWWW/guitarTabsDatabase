import glob
import json
import csv
from collections import defaultdict
from mingus.core import notes
from mingus.core.mt_exceptions import NoteFormatError


def compute_transition_probabilities(sequences, include_start=False):
    """
    Given a list of chord sequences (each a list of chord names),
    compute transition probabilities between chords, plus an 'END' state.
    If include_start is True, also count a 'START' → first_chord transition.
    Returns a dict of dicts: { curr_chord: { next_chord_or_'END': probability, … }, … }
    """
    counts = defaultdict(lambda: defaultdict(int))
    endings = defaultdict(int)

    if include_start:
        for seq in sequences:
            if seq:
                counts['START'][seq[0]] += 1

    for seq in sequences:
        for i, chord in enumerate(seq):
            if i + 1 < len(seq):
                counts[chord][seq[i+1]] += 1
            else:
                endings[chord] += 1

    probabilities = {}
    for curr, next_counts in counts.items():
        total = sum(next_counts.values()) + endings.get(curr, 0)
        probs = {nxt: cnt/total for nxt, cnt in next_counts.items()}
        if endings.get(curr, 0) > 0:
            probs['END'] = endings[curr] / total
        probabilities[curr] = probs

    return probabilities


def transpose_chord_roots(chord_list, old_key, new_key):
    """
    Transpose the root of each chord in chord_list from old_key to new_key.
    Ignores any chord-quality suffix (e.g. 'Maj', 'm', '7', etc.).
    """
    semitone_shift = (notes.note_to_int(new_key) - notes.note_to_int(old_key)) % 12
    transposed = []
    for chord in chord_list:
        if len(chord) >= 2 and chord[1] in ('#', 'b'):
            root = chord[:2]
        else:
            root = chord[0]
        original_val = notes.note_to_int(root)
        new_val = (original_val + semitone_shift) % 12
        new_root = notes.int_to_note(new_val)
        transposed.append(new_root)
    return transposed


if __name__ == "__main__":
    # Locate JSON files
    file_paths = glob.glob("out_structure3/db_*.json")
    loaded_count = len(file_paths)
    print(f"Loaded {loaded_count} files.")

    # ---- Full-song analysis ----
    sequences_all = []
    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            chords_c = data.get("all-chords-in-c", [])
            if len(chords_c) > 4:
                sequences_all.append(chords_c)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Skipping {path}: file error ({e})")
    kept_all = len(sequences_all)
    print(f"Full-song: kept {kept_all} sequences.")

    freq_all = defaultdict(int)
    for seq in sequences_all:
        for chord in seq:
            freq_all[chord] += 1
    valid_chords_all = {ch for ch, cnt in freq_all.items() if cnt > 500}

    probs_all = compute_transition_probabilities(sequences_all, include_start=True)
    chromatic_roots = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    ordered_roots_all = [r for r in chromatic_roots if r in valid_chords_all]
    desired_order_all = ['START'] + ordered_roots_all + ['END']

    with open('csv/chord_transitions_full.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([''] + desired_order_all)
        for nxt in desired_order_all:
            row = [nxt] + [f"{probs_all.get(curr, {}).get(nxt, 0.0):.4f}" for curr in desired_order_all]
            writer.writerow(row)
    print("Saved chord_transitions_full.csv")

    # ---- Sectional analyses ----
    sections = ['intro', 'verse', 'chorus', 'bridge', 'pre-chorus', 'instrumental', 'solo', 'outro']
    for sec in sections:
        sequences_sec = []
        for path in file_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                old_key = data.get('key')
                for section, chords in data.get('components', {}).items():
                    if section.lower().startswith(sec) and len(chords) > 4:
                        transposed = transpose_chord_roots(chords, old_key, 'C')
                        sequences_sec.append(transposed)
                        break  # only first matching section per file
            except NoteFormatError as e:
                print(f"Skipping {path}: invalid chord ({e})")
                break  # skip entire file for this section
            except (json.JSONDecodeError, IOError) as e:
                print(f"Skipping {path}: file error ({e})")
                break
        kept_sec = len(sequences_sec)
        print(f"{sec.title()}: kept {kept_sec} sequences.")

        # Filter by frequency > 500
        freq_sec = defaultdict(int)
        for seq in sequences_sec:
            for chord in seq:
                freq_sec[chord] += 1
        valid_chords_sec = [r for r in chromatic_roots if r in freq_sec and freq_sec[r] > 500]

        probs_sec = compute_transition_probabilities(sequences_sec, include_start=True)
        desired_order_sec = ['START'] + valid_chords_sec + ['END']

        fname = f"csv/chord_transitions_{sec.replace('-', '_')}.csv"
        with open(fname, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([''] + desired_order_sec)
            for nxt in desired_order_sec:
                row = [nxt] + [f"{probs_sec.get(curr, {}).get(nxt, 0.0):.4f}" for curr in desired_order_sec]
                writer.writerow(row)
        print(f"Saved {fname}")
