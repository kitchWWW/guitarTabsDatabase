from mingus.core.chords import from_shorthand
from mingus.core.scales import get_notes

def identify_key(chord_list):
    """
    Identify the most likely major key for a list of chord shorthands.
    Args:
        chord_list (list of str]): e.g. ["CMaj", "Gmaj", "Amin", "Fmaj"]
    Returns:
        str: the tonic of the best-matching major key, e.g. "C"
    """
    # All twelve major keys (you can swap in flats if you prefer)
    major_keys = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    # Initialize a score counter for each key
    key_scores = {key: 0 for key in major_keys}

    for chord in chord_list:
        try:
            notes = from_shorthand(chord)
        except Exception:
            # If Mingus can't parse the chord shorthand, skip it
            continue

        for key in major_keys:
            # get_notes(tonic, scale_type) → the 7 notes of that major scale
            scale_notes = get_notes(key)
            # Count how many chord-tones fall into this scale
            key_scores[key] += sum(1 for n in notes if n in scale_notes)

    # Return the key with the highest total score
    return max(key_scores, key=key_scores.get)


if __name__ == "__main__":
    chord_list = ["FMaj", "Gm", "Amin", "FM7"]
    key = identify_key(chord_list)
    print(f"The most likely key is: {key}")
