import json
import glob
import re
import numpy as np
import statistics

# Precompiled regular expressions.
MAJOR_PATTERN = re.compile(r'^[A-G](#|b)?(maj)?$', flags=re.IGNORECASE)
MINOR_PATTERN = re.compile(r'^[A-G](#|b)?m$', flags=re.IGNORECASE)

def is_chromatic(chord):
    """
    Returns True if a chord is considered chromatic.
    
    A chord is non-chromatic (returns False) if:
      - It is an inversion (contains a slash, e.g. "C#m/E")
      - It is a plain major chord (e.g. "C", "F", "Amaj")
      - It is a plain minor chord (e.g. "Am", "C#m")
    
    Otherwise, returns True (it has alterations such as 7, add9, etc.).
    """
    chord = chord.strip()
    if MAJOR_PATTERN.match(chord):
        return False
    if MINOR_PATTERN.match(chord):
        return False
    return True

def compute_chromaticness(chords):
    """
    Given a list of chords, computes the ratio of unique chords that are chromatic.
    Returns a float between 0 and 1.
    """
    unique = set(chords)
    if not unique:
        return 0.0
    chromatic_count = sum(1 for chord in unique if is_chromatic(chord))
    return chromatic_count / len(unique)

def compute_summary_stats(data):
    """
    Given a list of numbers, computes a dictionary with:
      - average ("avg")
      - mode ("mode") – in case of multiple modes, uses the smallest value
      - minimum ("min")
      - maximum ("max")
      - first quartile ("q1")
      - third quartile ("q3")
    If data is empty, returns None for each stat.
    """
    if not data:
        return {"avg": None, "mode": None, "min": None, "max": None, "q1": None, "q3": None}
    avg = sum(data) / len(data)
    try:
        mode_val = statistics.mode(data)
    except statistics.StatisticsError:
        mode_val = min(statistics.multimode(data))
    mn = min(data)
    mx = max(data)
    q1 = float(np.percentile(data, 25))
    q3 = float(np.percentile(data, 75))
    return {"avg": avg, "mode": mode_val, "min": mn, "max": mx, "q1": q1, "q3": q3}

def analyze_songs_detailed(song_files):
    """
    Process a list of JSON song files and compute detailed summary stats.
    
    Only songs with at least one non-empty verse and one non-empty chorus are kept.
    For each section type (verses, choruses, bridges, pre-choruses, intros, outros),
    and for each song (across all sections), we record:
      - Total chord count,
      - Unique chord count,
      - Chromaticness (ratio of unique chords that have chromatic alterations).
    
    Additionally, we record per song counts of the number of verses, choruses, bridges,
    pre-choruses, intros, and outros. For verses and choruses (present in every song
    by definition), we also compute the number of shared unique chords.
    
    For every metric (for example, chords per verse) we then compute summary statistics:
        average, mode, min, max, Q1, and Q3.
    
    Returns a dictionary of summary stats.
    """
    # These dictionaries will hold per-instance metric values.
    metrics = {
        "verse": {"chords": [], "unique": [], "chromatic": []},
        "chorus": {"chords": [], "unique": [], "chromatic": []},
        "bridge": {"chords": [], "unique": [], "chromatic": []},
        "prechorus": {"chords": [], "unique": [], "chromatic": []},
        "intro": {"chords": [], "unique": [], "chromatic": []},
        "outro": {"chords": [], "unique": [], "chromatic": []}
    }
    
    # Song-level metrics.
    song_metrics = {"chords": [], "unique": [], "chromatic": [], "shared": []}
    # Song-level counts for section instances.
    song_counts = {
        "verses": [],
        "choruses": [],
        "bridges": [],
        "prechoruses": [],
        "intros": [],
        "outros": []
    }
    
    songs_kept = []
    # Load JSON files and filter out those that lack at least one non-empty verse and chorus.
    for filepath in song_files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            continue
        
        print(data.items())

        verses = {k: v for k, v in data.items() if k.lower().startswith("verse") and v}
        choruses = {k: v for k, v in data.items() if k.lower().startswith("chorus") and v}
        if verses and choruses:
            songs_kept.append(data)
    
    if not songs_kept:
        print("No songs with at least one non-empty verse and one non-empty chorus were found.")
        return {}
    
    # Process each valid song.
    for song in songs_kept:
        # Filter sections by type (only non-empty ones).
        # print(song.items()
        pass
        # verses = {k: v for k, v in song.items() if k.lower().startswith("verse") and v}
        # choruses = {k: v for k, v in song.items() if k.lower().startswith("chorus") and v}
        # bridges = {k: v for k, v in song.items() if k.lower().startswith("bridge") and v}
        # pre_choruses = {k: v for k, v in song.items() if k.lower().startswith("pre-chorus") and v}
        # intros = {k: v for k, v in song.items() if k.lower().startswith("intro") and v}
        # outros = {k: v for k, v in song.items() if k.lower().startswith("outro") and v}



# Example usage:
if __name__ == "__main__":
    song_files = glob.glob("out_structure_and_chords/*.txt")
    detailed_stats = analyze_songs_detailed(song_files)
    
    # if detailed_stats:
    #     import pprint
    #     pprint.pprint(detailed_stats)