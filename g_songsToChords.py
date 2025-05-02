import os
import re
import json

from keyid import identify_key

# -- at top of file, replace your FLAT_TO_SHARP with a full enharmonic map --

# Map any two‐character enharmonic (flats, rare sharps, etc.) to our 12-note sharp list
ENHARMONIC_EQUIVALENTS = {
    'Cb': 'B',  'Fb': 'E',
    'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#',
    'B#': 'C',  'E#': 'F'
}

CHROMATIC_SHARPS = ['C', 'C#', 'D', 'D#', 'E', 'F',
                    'F#', 'G', 'G#', 'A', 'A#', 'B']

def note_to_semitone(note):
    # Extract just the root letter plus accidental (if any)
    m = re.match(r'^([A-G](?:#|b)?)', note)
    if not m:
        raise ValueError(f"Unrecognized note name: {note!r}")
    root = m.group(1)
    # Normalize to our sharps-only list
    root = ENHARMONIC_EQUIVALENTS.get(root, root)
    return CHROMATIC_SHARPS.index(root)

def transpose_chord_roots(chord_list, old_key, new_key):
    """
    Transpose only the root of each chord in chord_list from old_key to new_key.
    Returns a list of new roots in uppercase (no quality suffix).
    """
    interval = (note_to_semitone(new_key) - note_to_semitone(old_key)) % 12
    transposed = []
    for chord in chord_list:
        m = re.match(r'^([A-G](?:#|b)?)', chord)
        if not m:
            transposed.append(chord)  # no recognizable root
            continue
        root = m.group(1)
        sem = note_to_semitone(root)
        new_root = CHROMATIC_SHARPS[(sem + interval) % 12]
        transposed.append(new_root)
    return transposed


# -- New helper for transposition --
CHROMATIC_SHARPS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
FLAT_TO_SHARP = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}

# -- Your existing parser unchanged --
def parse_file(content):
    """
    Parses the file content to detect song sections (e.g. intro, verse, chorus, etc.)
    and extracts chords contained in the [ch]...[/ch] markers.

    Returns:
        A dict with three keys:
          - 'order': a list of section keys in appearance order
          - 'components': a mapping of section keys to arrays of chords
          - 'all-chords': a list of every chord in the song in order
    """
    header_pattern = re.compile(
        r'(?i)(?:^\s*|\[)\s*(?P<section>intro|verse|chorus|bridge|pre-chorus|instrumental|solo|outro|coro|pre-coro)'
        r'(?:\s*(?P<number>\d+))?\s*(?:\]|:|-|\.\s+)',
        re.MULTILINE
    )
    matches = list(header_pattern.finditer(content))
    if not matches:
        return {'order': [], 'components': {}, 'all-chords': []}

    translation = {'coro': 'chorus', 'pre-coro': 'pre-chorus'}
    sections_dict = {}
    for i, match in enumerate(matches):
        raw = match.group('section').lower()
        sec = translation.get(raw, raw)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        snippet = content[start:end]
        chords = re.findall(r'\[ch\](.+?)\[/ch\]', snippet, flags=re.IGNORECASE)
        chords = [c.strip() for c in chords]
        sections_dict.setdefault(sec, []).append(chords)

    components = {}
    for sec, lists in sections_dict.items():
        if len(lists) == 1:
            components[sec] = lists[0]
        else:
            for idx, cl in enumerate(lists, start=1):
                components[f"{sec}-{idx}"] = cl

    order, counts = [], {}
    for match in matches:
        raw = match.group('section').lower()
        sec = translation.get(raw, raw)
        counts[sec] = counts.get(sec, 0) + 1
        key = f"{sec}-{counts[sec]}" if len(sections_dict[sec]) > 1 else sec
        order.append(key)

    all_chords = []
    for key in order:
        all_chords.extend(components.get(key, []))

    return {'order': order, 'components': components, 'all-chords': all_chords}


def process_files(input_dir, output_dir):
    """
    Processes each .txt file in input_dir, identifies the song key,
    and writes JSON with structure preserving section order plus key
    and transposed chords.
    """
    os.makedirs(output_dir, exist_ok=True)
    for fname in os.listdir(input_dir):
        if not fname.endswith('.txt'):
            continue
        in_path = os.path.join(input_dir, fname)
        out_path = os.path.join(output_dir, fname.replace('.txt', '.json'))
        with open(in_path, 'r', encoding='utf-8') as f:
            content = f.read()

        parsed = parse_file(content)
        # Identify the likely key from all chords
        detected_key = identify_key(parsed['all-chords'])
        parsed['key'] = detected_key
        # Transpose every chord root into C major
        parsed['all-chords-in-c'] = transpose_chord_roots(
            parsed['all-chords'],
            old_key=detected_key,
            new_key='C'
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(parsed, f, indent=4)

        print(f"Processed {fname} -> {out_path} (key: {detected_key})")


if __name__ == '__main__':
    process_files('data', 'out_structure3')
