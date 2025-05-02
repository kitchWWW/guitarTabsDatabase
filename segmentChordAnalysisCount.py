import os
import glob
import json
import csv
from collections import defaultdict
from mingus.core import notes
from mingus.core.mt_exceptions import NoteFormatError


def compute_transition_counts(sequences, include_start=False):
    """
    Given a list of chord sequences (each a list of chord names),
    compute raw transition counts between chords plus an 'END' state.
    If include_start is True, also count a 'START' → first_chord transition.
    Returns a dict of dicts: { curr_chord: { next_chord_or_'END': count, … }, … }
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

    # Add END counts
    for curr, end_count in endings.items():
        counts[curr]['END'] = end_count

    return counts


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
    # Load list of files to keep
    with open("kept_songs.txt", "r", encoding="utf-8") as f:
        files_kept = set(json.load(f))      # e.g. ["db_123.json", "db_456.json", ...]

    # Find all JSONs in out_structure3 and filter
    all_paths = glob.glob("out_structure/db_*.json")
    file_paths = [p for p in all_paths if p in files_kept]

    # ---- Full-song analysis ----
    sequences_all = []
    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            chords_c = data.get("all-chords-in-c", [])
            if len(chords_c) >= 2:
                sequences_all.append(chords_c)
        except (json.JSONDecodeError, IOError):
            continue

    # Compute raw counts
    counts_all = compute_transition_counts(sequences_all, include_start=True)

    chromatic_roots = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    desired_order_all = ['START'] + chromatic_roots + ['END']

    # Write full counts CSV
    os.makedirs('csv', exist_ok=True)
    with open('csvTransitionCount/chord_transitions_full.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([''] + desired_order_all)
        for nxt in desired_order_all:
            row = [nxt] + [counts_all.get(curr, {}).get(nxt, 0) for curr in desired_order_all]
            writer.writerow(row)
    print("Saved csvTransitionCount/chord_transitions_full.csv")

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
            except (NoteFormatError, json.JSONDecodeError, IOError):
                continue

        # Compute raw counts for section
        counts_sec = compute_transition_counts(sequences_sec, include_start=True)

        # Determine valid chords present
        freq_sec = defaultdict(int)
        for seq in sequences_sec:
            for chord in seq:
                freq_sec[chord] += 1
        valid_chords_sec = [r for r in chromatic_roots if freq_sec.get(r, 0) > 0]

        desired_order_sec = ['START'] + valid_chords_sec + ['END']
        fname = f'csvTransitionCount/chord_transitions_{sec.replace('-', '_')}.csv'
        with open(fname, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([''] + desired_order_sec)
            for nxt in desired_order_sec:
                row = [nxt] + [counts_sec.get(curr, {}).get(nxt, 0) for curr in desired_order_sec]
                writer.writerow(row)
        print(f"Saved {fname}")
