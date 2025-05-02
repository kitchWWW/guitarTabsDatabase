from mingus.core import notes

def transpose_chord_roots(chord_list, old_key, new_key):
    """
    Transpose the root of each chord in chord_list from old_key to new_key.
    Ignores any chord-quality suffix (e.g. 'Maj', 'm', '7', etc.).
    """
    # Compute how many semitones to shift
    semitone_shift = (notes.note_to_int(new_key) - notes.note_to_int(old_key)) % 12

    transposed = []
    for chord in chord_list:
        # Grab the root note (letter plus optional accidental)
        if len(chord) >= 2 and chord[1] in ('#', 'b'):
            root = chord[:2]
            rest = chord[2:]
        else:
            root = chord[0]
            rest = chord[1:]

        # Transpose root
        original_val = notes.note_to_int(root)
        new_val = (original_val + semitone_shift) % 12
        new_root = notes.int_to_note(new_val)

        # Since we’re ignoring quality, just append the new_root
        transposed.append(new_root)

    return transposed

# Example usage:
chord_list = ["FMaj", "Gm", "Amin", "FM7"]
print(transpose_chord_roots(chord_list, old_key="F", new_key="C"))
# → ['C', 'D', 'E', 'C']
